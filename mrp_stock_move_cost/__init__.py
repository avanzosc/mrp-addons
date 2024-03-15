from . import models
from odoo import api, SUPERUSER_ID


def _post_install_put_cost_in_productions(cr, registry):
    """
        This method will create a salary journal for each company and allocate it to each Belgian structure.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    productions = env["mrp.production"].search(
        [("state", "=", "done")])
    for production in productions:
        production.update_prodution_cost()
