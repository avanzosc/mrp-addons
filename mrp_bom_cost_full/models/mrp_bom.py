# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _default_overhead(self):
        return float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mrp_bom_overhead", default=15)
        )

    overhead = fields.Float(
        min_display_digits="Product Price",
        default=_default_overhead,
    )
    total_cost_without_overhead = fields.Float(
        min_display_digits="Product Price",
        compute="_compute_total_cost_without_owerhead",
        store=True,
    )
    total_cost_with_overhead = fields.Float(
        min_display_digits="Product Price",
        compute="_compute_total_cost_with_owerhead",
        store=True,
    )

    @api.onchange("overhead")
    def onchange_overhead(self):
        self.bom_line_ids.write({"overhead": self.overhead})
        self.operation_ids.write({"overhead": self.overhead})

    @api.depends(
        "bom_line_ids",
        "bom_line_ids.cost_without_overhead",
        "operation_ids",
        "operation_ids.cost_op_without_overhead",
    )
    def _compute_total_cost_without_owerhead(self):
        for bom in self:
            bom.total_cost_without_overhead = sum(
                bom.bom_line_ids.mapped("cost_without_overhead")
            ) + sum(bom.operation_ids.mapped("cost_op_without_overhead"))

    @api.depends(
        "bom_line_ids",
        "bom_line_ids.cost_with_overhead",
        "operation_ids",
        "operation_ids.cost_op_with_overhead",
    )
    def _compute_total_cost_with_owerhead(self):
        for bom in self:
            bom.total_cost_with_overhead = sum(
                bom.bom_line_ids.mapped("cost_with_overhead")
            ) + sum(bom.operation_ids.mapped("cost_op_with_overhead"))
