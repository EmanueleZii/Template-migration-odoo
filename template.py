import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Funzione principale di migrazione.
    :param cr: cursore del database (per SQL)
    :param version: versione attuale installata (stringa)
    """
    if not version:
        return

    # Inizializza l'ambiente Odoo
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info("Inizio migrazione modulo: versione precedente %s", version)

    # --- 1. LOGICA SQL (Veloce e sicura) ---
    # Usalo per rinominare colonne o sistemare dati grezzi
    query = """
        UPDATE mio_modello
        SET stato = 'draft'
        WHERE stato IS NULL
    """
    cr.execute(query)

    # --- 2. LOGICA ORM (Semplice ma più lenta) ---
    # Usalo se devi chiamare metodi del modello o logiche complesse
    records = env['mio.modello'].search([('campo_nuovo', '=', False)])
    for rec in records:
        try:
            # Esempio: calcola un valore basato su altri campi
            rec.campo_nuovo = rec.valore_vecchio * 1.2
        except Exception as e:
            _logger.error("Errore sul record %s: %s", rec.id, e)

    _logger.info("Migrazione completata con successo.")
