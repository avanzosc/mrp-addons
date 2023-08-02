# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, company_id, values, bom):
        mo_values = super(StockRule, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name, origin,
            company_id, values, bom)
        if "origin" in mo_values and mo_values.get("origin", False):
            cond = [("name", "=", mo_values.get("origin"))]
            sale = self.env["sale.order"].search(cond, limit=1)
            if sale:
                origin = sale.name
                if sale.origin:
                    origin = "{} // {}".format(origin, sale.origin)
                if sale.client_order_ref:
                    origin = "{} // {}".format(origin, sale.client_order_ref)
                mo_values["origin"] = origin
        return mo_values
