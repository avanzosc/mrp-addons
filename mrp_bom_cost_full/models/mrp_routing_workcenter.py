# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    time_cycle = fields.Float(readonly=False)
    time_cycle_manual = fields.Float(default=1)
    hour_cost = fields.Float(
        digits="Product Price",
    )
    cost_op_without_overhead = fields.Float(
        digits="Product Price",
        compute="_compute_cost_op_without_overhead",
        store=True,
    )
    overhead = fields.Float(
        string="Overhead %",
        digits="Product Price",
    )
    cost_op_with_overhead = fields.Float(
        digits="Product Price",
        compute="_compute_cost_op_with_overhead",
        store=True,
    )

    @api.onchange("workcenter_id")
    def onchange_workcenter_id(self):
        self.hour_cost = self.workcenter_id.costs_hour if self.workcenter_id else 0.0

    @api.depends("time_cycle", "hour_cost")
    def _compute_cost_op_without_overhead(self):
        for workcenter in self:
            workcenter.cost_op_without_overhead = (
                workcenter.time_cycle * workcenter.hour_cost
            )

    @api.depends("cost_op_without_overhead", "overhead")
    def _compute_cost_op_with_overhead(self):
        for workcenter in self:
            if not workcenter.overhead:
                workcenter.cost_op_with_overhead = workcenter.cost_op_without_overhead
            else:
                workcenter.cost_op_with_overhead = (
                    workcenter.cost_op_without_overhead
                    * (1 + workcenter.overhead / 100.0)
                )
