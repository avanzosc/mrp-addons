# Copyright 2022 Patxi lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    duration_estimated = fields.Float(
        string="Expected Duration",
        compute="_compute_duration_estimated",
        copy=False,
        store=True,
    )
    duration = fields.Float(
        string="Real Duration",
        compute="_compute_duration",
        copy=False,
        store=True,
    )

    @api.depends("workorder_ids", "workorder_ids.duration_expected")
    def _compute_duration_estimated(self):
        for production in self:
            production.duration_estimated = sum(
                production.mapped("workorder_ids.duration_expected")
            )

    @api.depends("workorder_ids", "workorder_ids.duration")
    def _compute_duration(self):
        for production in self:
            production.duration = sum(production.mapped("workorder_ids.duration"))
