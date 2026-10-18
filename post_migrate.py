# ESEGUI IN ODOO SHELL (db in manutenzione)
# o incapsula in un post-migration script del tuo modulo.

from datetime import date, timedelta
from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

DRY_RUN = False  # Metti True per provare senza committare

def _daterng_ok(start, end):
    if not start:
        return False
    if end and end < start:
        return False
    return True

def _overlap(a_start, a_end, b_start, b_end):
    a_end = a_end or date.max
    b_end = b_end or date.max
    return not (a_end < b_start or b_end < a_start)

def migrate_contracts_to_versions(env):
    Contract = env['hr.contract'].with_context(active_test=False)
    Employee = env['hr.employee'].with_context(active_test=False)
    Version  = env['hr.version']

    # 1) Prendi tutti i contratti (senza filtrare per state!)
    all_contracts = Contract.search([], order='employee_id, date_start, id')

    # 2) Mappa contratti per dipendente
    by_emp = {}
    for c in all_contracts:
        by_emp.setdefault(c.employee_id.id, []).append(c)

    created = 0
    mapping = {}  # old_contract_id -> new_version_id
    bad_ranges = []
    with env.cr.savepoint():
        for emp_id, contracts in by_emp.items():
            last_end = None
            for c in contracts:
                start = c.date_start or (c.create_date and c.create_date.date())
                end   = c.date_end or False

                # Normalizza date e impedisci overlap: se la nuova inizia
                # prima o uguale alla fine precedente, sposta all'indomani.
                if last_end and start and start <= last_end:
                    start = last_end + timedelta(days=1)

                if not _daterng_ok(start, end):
                    bad_ranges.append((c.id, start, end))
                    continue

                vals = {
                    'employee_id': c.employee_id.id,
                    'date_version': start,
                    'date_end': end,
                    # Campi tipici payroll/HR che devono versionare (adatta se usi localizzazioni):
                    'wage': getattr(c, 'wage', False),
                    'job_id': c.job_id.id if c.job_id else False,
                    'department_id': c.department_id.id if c.department_id else False,
                    'resource_calendar_id': c.resource_calendar_id.id if c.resource_calendar_id else False,
                }
                v = Version.create(vals)
                mapping[c.id] = v.id
                created += 1

                if end:
                    last_end = end

        # 3) Validazioni base
        # 3.1 Nessuna sovrapposizione per employee
        overlap_found = []
        for emp in Employee.search([]):
            vset = env['hr.version'].search([('employee_id', '=', emp.id)], order='date_version, id')
            for i in range(len(vset) - 1):
                a, b = vset[i], vset[i+1]
                if _overlap(a.date_version, a.date_end, b.date_version, b.date_end):
                    overlap_found.append((emp.id, a.id, b.id))

        # 3.2 Confronto volumi
        old_count = len(all_contracts)
        new_count = env['hr.version'].search_count([])

        _logger.info("Migrazione: creati %s hr.version da %s hr.contract", created, old_count)
        _logger.info("Mapping contratti->versioni: %s righe", len(mapping))
        _logger.info("Range non validi: %s; Overlap trovati: %s", len(bad_ranges), len(overlap_found))

        # 4) Se dry-run, rollback
        if DRY_RUN:
            raise RuntimeError("Dry run: stop e rollback volontario.")

    # 5) Stampa/ritorna summary utili
    return {
        'created_versions': created,
        'old_contracts': old_count,
        'invalid_ranges': bad_ranges,
        'overlaps': overlap_found,
        'mapping': mapping,  # tienilo per toccare riferimenti custom
    }

# ESECUZIONE
env = api.Environment(env.cr, SUPERUSER_ID, {})
summary = migrate_contracts_to_versions(env)
print("=== SUMMARY MIGRAZIONE ===")
for k, v in summary.items():
    if k != 'mapping':
        print(k, ":", v)
print("Esempio mapping (primi 10):", list(list(summary['mapping'].items())[:10]))
