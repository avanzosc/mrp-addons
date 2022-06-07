# Copyright 2022 Patxi lersundi 
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit= 'mrp.production'

    total_duration_estimated = fields.Float(
        string="Total duration estimated", store=True, copy=False,
        compute="_compute_total_duration_estimated")
    total_duration = fields.Float(
        string="Total duration", store=True, copy=False,
        compute="_compute_total_duration")

    @api.depends("workorder_ids", "workorder_ids.duration_expected")
    def _compute_total_duration_estimated(self):
        for production in self:
            production.total_duration_estimated = (
                sum(production.workorder_ids.mapped('duration_expected')))

    @api.depends("workorder_ids", "workorder_ids.duration")
    def _compute_total_duration(self):
        for production in self:
            production.total_duration = (
                sum(production.workorder_ids.mapped('duration')))
