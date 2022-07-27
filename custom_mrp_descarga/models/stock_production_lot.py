# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    average_price = fields.Float(
        string="Average Price",
        compute="_compute_average_price")
    move_line_ids = fields.One2many(
        string="Move Lines With Applied Prices",
        comodel_name="stock.move.line",
        inverse_name="lot_id")

    def _compute_average_price(self):
        for line in self:
            line.average_price = 0
            movelines = self.env["stock.move.line"].search(
                [("product_id", "=", line.product_id.id),
                 ("lot_id", "=", line.id), ("production_id", "!=", False)])
            if movelines:
                amount_total = sum(movelines.mapped("amount"))
                if line.product_qty != 0:
                    line.average_price = amount_total / line.product_qty

    def action_view_move_lines(self):
        context = self.env.context.copy()
        context.update({"default_lot_id": self.id})
        return {
            "name": _("Move Lines"),
            "view_mode": "tree,form",
            "res_model": "stock.move.line",
            "domain": [("product_id", "=", self.product_id.id),
                       ("id", "in", self.move_line_ids.ids),
                       ("applied_price", ">", 0)],
            "type": "ir.actions.act_window",
            "context": context
        }
