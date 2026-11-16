# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    material_cost = fields.Float(
        digits="Product Price",
    )
    cost_without_overhead = fields.Float(
        digits="Product Price",
        compute="_compute_cost_without_overhead",
        store=True,
    )
    overhead = fields.Float(
        string="Overhead %",
        digits="Product Price",
    )
    cost_with_overhead = fields.Float(
        digits="Product Price",
        compute="_compute_cost_with_overhead",
        store=True,
    )

    @api.onchange("product_id")
    def onchange_product_id(self):
        result = super().onchange_product_id()
        self.material_cost = self.product_id.standard_price if self.product_id else 0.0
        return result

    @api.depends("product_qty", "material_cost")
    def _compute_cost_without_overhead(self):
        for line in self:
            line.cost_without_overhead = line.product_qty * line.material_cost

    @api.depends("cost_without_overhead", "overhead")
    def _compute_cost_with_overhead(self):
        for line in self:
            if not line.overhead:
                line.cost_with_overhead = line.cost_without_overhead
            else:
                line.cost_with_overhead = line.cost_without_overhead * (
                    1 + line.overhead / 100.0
                )
