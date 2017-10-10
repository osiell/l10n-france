import logging
import re

from openerp import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if version:
        migrate_ape_xml_id(env)

def migrate_ape_xml_id(env):
    logger.info("[UDPATE res.partner.category] Correction category_id for ape")

    data_records = env['ir.model.data'].search([
        ('model', '=', 'res.partner.category'),
        ('res_id', '!=', False),
        ('name', 'ilike', 'nace'),
        ('module', '=', 'l10n_fr_naf_ape'),
        ])

    category_model = env['res.partner.category']
    naf_categ_ids = data_records.mapped('res_id')
    naf_categs = category_model.browse(naf_categ_ids)

    res_partners = env['res.partner'].search([
        '|', ('active', '=', True), ('active', '=', False),
        ('category_id', '!=', False),
        ('category_id', 'in', naf_categ_ids)
        ])

    for partner in res_partners:
        # if re.match("^\[.*\]", category.name):
        #     nace_code = category.name.split("[")[1].split("]")[0]
        category_ids = category_model.browse()
        for category in partner.category_id:
            if category in naf_categs:
                if re.match("^\[.*\]", category.parent_id.name):
                    naf_code = category.parent_id.name.split("[")[1].split("]")[0]
                    naf = session.env['res.partner.nace'].search([('code', '=', naf_code)])
                    naf.ensure_one()
                    partner.ape_id = naf
                    category_ids += category
                    category.active= False
    data_records.unlink()
