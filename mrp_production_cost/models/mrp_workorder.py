# Copyright 2022 Patxi Lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    workorder_cost_estimated = fields.Float(
        string="Estimated Cost",
        copy=False,
        store=True,
        compute="_compute_workorder_cost_estimated",
    )
    workorder_cost_real = fields.Float(
        string="Real Cost",
        copy=False,
        store=True,
        compute="_compute_workorder_cost_real",
    )

    @api.depends("duration_expected", "costs_hour")
    def _compute_workorder_cost_estimated(self):
        for order in self:
            workorder_cost_estimated = 0
            if order.duration_expected:
                workorder_cost_estimated = order.costs_hour * (
                    order.duration_expected / 60
                )
            order.workorder_cost_estimated = workorder_cost_estimated

    @api.depends("duration", "costs_hour")
    def _compute_workorder_cost_real(self):
        for order in self:
            workorder_cost_real = 0
            if order.duration:
                workorder_cost_real = order.costs_hour * (order.duration / 60)
            order.workorder_cost_real = workorder_cost_real
