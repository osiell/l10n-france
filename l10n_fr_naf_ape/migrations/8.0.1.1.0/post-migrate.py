import logging
import re

from openerp import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if version:
        with openerp.api.Environment.manage():
            with openerp.registry(env.cr.dbname).cursor() as new_cr:
                new_env = openerp.api.Environment(new_cr, env.uid, env.context)
                move_old_naf_ape(new_env)

def move_old_naf_ape(env):
    logger.info("[UDPATE res.partner.category] Correction category_id for ape")

    data_records = env['ir.model.data'].search([
        ('model', '=', 'res.partner.category'),
        ('res_id', '!=', False),
        ('name', 'ilike', 'naf'),
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
        for category in partner.category_id:
            if category in naf_categs:
                if re.match("^\[.*\]", category.name):
                    naf_code = category.name.split("[")[1].split("]")[0]
                    naf = env['res.partner.nace'].search([('code', '=', naf_code)])
                    naf.ensure_one()
                    partner.ape_id = naf
    naf_categs.write({'active': False})
    data_records.unlink()
