# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=attribute-string-redundant
from odoo import _, api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    average_price = fields.Float(
        string="Average Price",
        digits="MRP Price Decimal Precision",
        compute="_compute_average_price",
    )

    @api.depends(
        "move_line_ids.amount", "move_line_ids.quantity", "move_line_ids.state"
    )
    def _compute_average_price(self):
        for line in self:
            average_price = 0
            clasified = line.move_line_ids.filtered(
                lambda c: c.state == "done"
                and (c.location_dest_id.usage == "internal")
                and (c.location_id.usage != "internal")
            )
            if clasified:
                amount_total = sum(clasified.mapped("amount"))
                quantity = sum(clasified.mapped("quantity"))
                if quantity != 0:
                    average_price = amount_total / quantity
            line.average_price = average_price

    def action_view_move_lines(self):
        context = self.env.context.copy()
        context.update({"default_lot_id": self.id})
        return {
            "name": _("Move Lines"),
            "view_mode": "list,form",
            "res_model": "stock.move.line",
            "domain": [
                ("product_id", "=", self.product_id.id),
                ("id", "in", self.move_line_ids.ids),
            ],
            "type": "ir.actions.act_window",
            "context": context,
        }
