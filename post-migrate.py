import logging
from odoo import api, SUPERUSER_ID


_logger = logging.getLogger(__name__)

def migrate(cr, version):
    env = api.Enviroment(cr, SUPERUSER_ID,{})
    
    query_data = """
    INSERT INTO hr_version(
        create_uid, create_date, name, employeeid, company_id,
        subscription_id, date_start, date_end, resource_calendar_id,
        wage, is_in_contract
    )
    SELECT c.create_uid, NOW(), c.name, c.employee_id, c.company_id,
    c.id,c.date_start, c.date_end, c.resource_calendar_id,
    c.wage, TRUE
    FROM hr_contract c
    WHERE c.x_migrated_to_version IS FALSE
    """
    
    cr.execute(query_data)
    
    query_attachment = """
    UPDATE ir_attachment att
    SET res_model ='hr.version'
    res_id = v.id
    FROM hr_version v
    WHERE att.res_model = 'hr.contract'
    AND att.res_id = v.subscription_id; 
    """
    
    cr.execute(query_attachment)
    
    cr.excute("UPDATE hr_contract SET x_migrated_to_version = TRUE, active = FALSE")
    _logger.info("Migrazione da Odoo 16 a 19 completata con successo.")