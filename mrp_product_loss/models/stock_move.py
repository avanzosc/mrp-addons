# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    to_consume_before_loss_qty = fields.Float(
        string="To Consume Before Loss Quantity",
        digits="Product Unit of Measure",
        default="0.0",
    )
    product_loss_qty = fields.Float(
        string="Loss Quantity", digits="Product Unit of Measure", default="0.0"
    )

    def calculate_raw_loss_qty(self):
        self.ensure_one()
        mo = self.raw_material_production_id
        bom = self.bom_line_id.bom_id
        product_loss = self.product_id.product_loss_qty
        loss_qty = 0.0

        if mo and bom and product_loss > 0:
            base_qty = mo.qty_producing if mo.qty_producing > 0 else mo.product_qty
            loss_qty = (product_loss / bom.product_qty) * base_qty
        return loss_qty

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        if self.raw_material_production_id:
            loss_qty = self.calculate_raw_loss_qty()
            self.product_loss_qty = loss_qty
        return moves
