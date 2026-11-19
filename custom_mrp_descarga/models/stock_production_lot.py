# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    average_price = fields.Float(
        digits="MRP Price Decimal Precision",
    )

    def action_view_move_lines(self):
        context = self.env.context.copy()
        context.update({"default_lot_id": self.id})
        return {
            "name": _("Move Lines"),
            "view_mode": "tree,form",
            "res_model": "stock.move.line",
            "domain": [
                ("product_id", "=", self.product_id.id),
                ("id", "in", self.move_line_ids.ids),
            ],
            "type": "ir.actions.act_window",
            "context": context,
        }
