from . import models
from odoo import api, SUPERUSER_ID


def _post_install_put_non_prototype_in_mrp_production(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    productions = env["mrp.production"].search([])
    if productions:
        productions.write({"is_prototype": False})
