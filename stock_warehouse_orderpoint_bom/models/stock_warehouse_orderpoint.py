# Copyright 2022 AlfredodelaFuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.onchange("route_id")
    def _onchange_route_id(self):
        result = super()._onchange_route_id()
        if self.product_id and self.route_id:
            self.get_default_bom()
        return result

    @api.model
    def create(self, vals):
        orderpoints = super().create(vals)
        for orderpoint in orderpoints.filtered(lambda z: not z.bom_id):
            orderpoint.get_default_bom()
        return orderpoints

    def get_default_bom(self):
        for orderpoint in self.filtered(
            lambda x: x.product_id
            and x.route_id
            and x.route_id.rule_ids
            and x.route_id.rule_ids[0].action == "manufacture"
        ):
            cond = [
                ("type", "=", "normal"),
                "&",
                "|",
                ("company_id", "=", self.env.company.id),
                ("company_id", "=", False),
                "|",
                ("product_id", "=", orderpoint.product_id.id),
                "&",
                ("product_id", "=", False),
                ("product_tmpl_id", "=", orderpoint.product_tmpl_id.id),
            ]
            bom = self.env["mrp.bom"].search(cond)
            if bom and len(bom) == 1:
                orderpoint.bom_id = bom[0].id
