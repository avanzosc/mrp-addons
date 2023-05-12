# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    average_price = fields.Float(
        string="Average Price",
        digits="MRP Price Decimal Precision",
        compute="_compute_average_price",
        store=True)

    @api.depends("move_line_ids", "move_line_ids.amount",
                 "move_line_ids.qty_done", "move_line_ids.state")
    def _compute_average_price(self):
        for line in self:
            line.average_price = 0
            clasified = line.move_line_ids.filtered(
                lambda c: c.state == "done" and (
                    c.location_dest_id.usage == "internal"))
            quartering = line.move_line_ids.filtered(
                lambda c: c.production_id and c.production_id.quartering)
            if clasified:
                amount_total = sum(clasified.mapped("amount"))
                qty_done = sum(clasified.mapped("qty_done"))
                if qty_done != 0:
                    line.average_price = amount_total / qty_done
                    if line.company_id.paasa:
                        for record in quartering:
                            if record.standard_price != line.average_price:
                                record.write({
                                    "standard_price": line.average_price,
                                    "amount": (
                                        line.average_price * record.qty_done)
                                    })

    def action_view_move_lines(self):
        context = self.env.context.copy()
        context.update({"default_lot_id": self.id})
        return {
            "name": _("Move Lines"),
            "view_mode": "tree,form",
            "res_model": "stock.move.line",
            "domain": [("product_id", "=", self.product_id.id),
                       ("id", "in", self.move_line_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }
