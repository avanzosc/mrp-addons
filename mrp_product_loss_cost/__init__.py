from . import models
from odoo import api, SUPERUSER_ID


def _post_install_put_cost_in_scrap(cr, registry):
    """
    This method will set the production cost on already done manufacturing orders.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    scraps = env["stock.scrap"].search([("state", "=", "done")])
    for scrap in scraps:
        scrap_unit_cost = scrap.product_id.standard_price
        if scrap.lot_id and scrap.lot_id.purchase_price:
            scrap_unit_cost = scrap.product_id.standard_price
        scrap.write(
            {
                "scrap_unit_cost": scrap_unit_cost,
                "scrap_cost": scrap_unit_cost * scrap.scrap_qty,
            }
        )
        if scrap.production_id and scrap.production_id.state == "done":
            scrap.production_id.update_prodution_cost()
