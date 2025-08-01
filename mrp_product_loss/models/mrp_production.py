# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def write(self, vals):
        res = super().write(vals)
        for move in self.move_raw_ids:
            loss_qty = move.calculate_raw_loss_qty()
            move.product_loss_qty = loss_qty
            if self.qty_producing > 0:
                move.to_consume_before_loss_qty = move.should_consume_qty - loss_qty
            else:
                move.to_consume_before_loss_qty = move.product_uom_qty - loss_qty
        return res

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        vals = super()._get_move_raw_values(
            product_id, product_uom_qty, product_uom, operation_id, bom_line
        )
        loss_qty = (
            product_id.product_loss_qty / bom_line.bom_id.product_qty
        ) * self.product_qty
        if bom_line:
            vals["to_consume_before_loss_qty"] = vals["product_uom_qty"]
            vals["product_uom_qty"] += loss_qty
            vals["product_loss_qty"] = loss_qty
        return vals
