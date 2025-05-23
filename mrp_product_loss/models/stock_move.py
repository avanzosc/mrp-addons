# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.tools import float_round


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

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if (
                "raw_material_production_id" in values
                and "product_id" in values
                and "product_uom_qty" in values
            ):
                product = self.env["product.product"].browse(values.get("product_id"))
                if product.product_loss_qty > 0:
                    new_qty = values.get("product_uom_qty") + product.product_loss_qty
                    values.update(
                        {
                            "product_uom_qty": new_qty,
                            "to_consume_before_loss_qty": values.get("product_uom_qty"),
                            "product_loss_qty": product.product_loss_qty,
                        }
                    )
        moves = super().create(vals_list)
        return moves

    @api.depends(
        "raw_material_production_id.qty_producing",
        "product_uom_qty",
        "product_uom",
        "to_consume_before_loss_qty",
        "product_loss_qty",
    )
    def _compute_should_consume_qty(self):
        result = super()._compute_should_consume_qty()
        for move in self:
            mo = move.raw_material_production_id
            if move.product_loss_qty > 0 and move.to_consume_before_loss_qty:
                new_qty = (
                    mo.qty_producing / mo.product_qty * move.to_consume_before_loss_qty
                    + move.product_loss_qty
                )
                move.should_consume_qty = float_round(
                    new_qty, precision_rounding=move.product_uom.rounding
                )
        return result
