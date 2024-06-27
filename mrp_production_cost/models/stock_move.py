# Copyright 2022 Patxi Lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_standard_cost = fields.Float(
        string="Standard Cost",
        readonly=True,
        store=True,
        copy=False,
        related="product_id.standard_price",
    )
    material_cost_to_consume = fields.Float(
        string="Material cost to consume",
        store=True,
        copy=False,
        compute="_compute_material_cost_to_consume",
    )
    material_cost_consumed = fields.Float(
        string="Material cost consumed",
        store=True,
        copy=False,
        compute="_compute_material_cost_consumed",
    )

    @api.depends("product_standard_cost", "product_uom_qty")
    def _compute_material_cost_to_consume(self):
        for move in self:
            move.material_cost_to_consume = (
                move.product_standard_cost * move.product_uom_qty
            )

    @api.depends("product_standard_cost", "quantity_done")
    def _compute_material_cost_consumed(self):
        for move in self:
            move.material_cost_consumed = (
                move.product_standard_cost * move.quantity_done
            )
