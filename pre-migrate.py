
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Creiamo una colonna temporanea 'migrated' su hr_contract 
    # per segnare i record processati e garantire l'idempotenza
    cr.execute("""
        ALTER TABLE hr_contract 
        ADD COLUMN IF NOT EXISTS x_migrated_to_version boolean DEFAULT FALSE
    """)