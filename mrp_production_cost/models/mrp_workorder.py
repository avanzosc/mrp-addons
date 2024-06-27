# Copyright 2022 Patxi Lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    machine_hour_cost = fields.Float(
        string="Machine hour cost",
        readonly=True,
        store=True,
        copy=False,
        related="workcenter_id.costs_hour",
    )
    workorder_cost_estimated = fields.Float(
        string="Workorder Cost estimated",
        copy=False,
        store=True,
        compute="_compute_workorder_cost_estimated",
    )
    workorder_cost_real = fields.Float(
        string="Workorder Cost real",
        copy=False,
        store=True,
        compute="_compute_workorder_cost_real",
    )

    @api.depends("duration_expected", "machine_hour_cost")
    def _compute_workorder_cost_estimated(self):
        for order in self:
            order.workorder_cost_estimated = (
                order.machine_hour_cost * order.duration_expected
            )

    @api.depends("duration", "machine_hour_cost")
    def _compute_workorder_cost_real(self):
        for order in self:
            order.workorder_cost_real = order.machine_hour_cost * order.duration
