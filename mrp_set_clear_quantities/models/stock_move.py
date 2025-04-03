# Copyright 2025 Berezi Amubieta - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        for move in self.filtered(
            lambda c: c.production_id or c.raw_material_production_id
        ):
            if (
                move.should_consume_qty
                and move.should_consume_qty < move.product_uom_qty
            ):
                super(StockMove, move)._action_assign(force_qty=move.should_consume_qty)
        return super()._action_assign(force_qty=force_qty)
