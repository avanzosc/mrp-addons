# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, values):
        result = super(StockMove, self).write(values)
        for line in self:
            manufacture = self.env.ref("mrp.route_warehouse0_manufacture")
            bom = self.env["mrp.bom"].search(
                [("product_tmpl_id", "=", line.product_id.product_tmpl_id.id)],
                limit=1)
            if "state" in values and values["state"] == "done" and (
                line.saca_line_id) and manufacture in (
                    line.product_id.route_ids) and bom and (
                        line.picking_id) and (line.picking_id.purchase_id):
                production = self.env["mrp.production"].create({
                    "bom_id": bom.id,
                    "product_id": line.product_id.id,
                    "product_uom_id": line.product_uom.id
                    })
                production._onchange_move_raw()
        return result
