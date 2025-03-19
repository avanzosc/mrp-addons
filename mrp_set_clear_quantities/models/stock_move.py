# Copyright 2025 Berezi Amubieta - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        res = super()._action_assign(force_qty=force_qty)
        for move in self.filtered(
            lambda x: x.production_id or x.raw_material_production_id
        ):
            if (
                move.should_consume_qty
                and move.should_consume_qty < move.product_uom_qty
                and move.state != "cancel"
            ):
                move.write(
                    {
                        "reserved_availability": move.should_consume_qty,
                        "quantity_done": move.should_consume_qty,
                    }
                )
        return res
