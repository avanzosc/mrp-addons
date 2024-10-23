# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def write(self, vals):
        result = super().write(vals)
        if "from_production" not in self.env.context and "purchase_price" in vals:
            for lot in self:
                lot._update_stock_move_lines()
        return result

    def _update_stock_move_lines(self):
        cond = [("lot_id", "=", self.id)]
        lines = self.env["stock.move.line"].search(cond)
        if lines:
            lines.write({"price_unit_cost": self.purchase_price})

        cond = [("lot_producing_id", "=", self.id)]
        productions = self.env["mrp.production"].search(cond)
        if productions:
            for production in productions:
                production.write(
                    {
                        "price_unit_cost": self.purchase_price,
                        "cost": self.purchase_price * production.qty_producing,
                    }
                )
