# Copyright 2022 Patxi Lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    estimated_material_cost_to_consume = fields.Float(
        string="Estimated Cost",
        store=True,
        copy=False,
        compute="_compute_estimated_material_cost_to_consume",
    )
    real_cost_consumed_material = fields.Float(
        string="Real Cost",
        store=True,
        copy=False,
        compute="_compute_real_cost_consumed_material",
    )

    @api.depends("price_unit", "product_uom_qty")
    def _compute_estimated_material_cost_to_consume(self):
        for move in self:
            move.estimated_material_cost_to_consume = (
                move.price_unit * move.product_uom_qty
            )

    @api.depends(
        "move_line_ids", "move_line_ids", "move_line_ids.state", "move_line_ids.cost"
    )
    def _compute_real_cost_consumed_material(self):
        for move in self:
            real_cost_consumed_material = 0
            lines = move.move_line_ids.filtered(lambda x: x.state == "done")
            if lines:
                real_cost_consumed_material = sum(lines.mapped("cost"))
            move.real_cost_consumed_material = real_cost_consumed_material
