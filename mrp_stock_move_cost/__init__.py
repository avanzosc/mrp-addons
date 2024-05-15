from . import models
from odoo import api, SUPERUSER_ID


def _post_install_put_cost_in_productions(cr, registry):
    """
    This method will set the production cost on already done manufacturing orders.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    productions = env["mrp.production"].search([("state", "=", "done")])
    for production in productions:
        production.update_prodution_cost()
