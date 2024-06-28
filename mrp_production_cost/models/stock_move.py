# Copyright 2022 Patxi Lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    material_cost_to_consume = fields.Float(
        string="Estimated Cost",
        store=True,
        copy=False,
        compute="_compute_material_cost_to_consume",
    )
    material_cost_consumed = fields.Float(
        string="Real Cost",
        store=True,
        copy=False,
        compute="_compute_material_cost_consumed",
    )

    @api.depends("price_unit", "product_uom_qty")
    def _compute_material_cost_to_consume(self):
        for move in self:
            move.material_cost_to_consume = move.price_unit * move.product_uom_qty

    @api.depends("price_unit", "quantity_done")
    def _compute_material_cost_consumed(self):
        for move in self:
            move.material_cost_consumed = move.price_unit * move.quantity_done
