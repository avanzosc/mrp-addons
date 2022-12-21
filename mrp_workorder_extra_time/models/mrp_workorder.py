# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    extra_time_piece = fields.Float(
        string="Extra time piece", copy=False)
    total_overtime = fields.Float(
        string="Total overtime", compute="_compute_total_overtime",
        store=True, copy=False)
    total_time = fields.Float(
        string="Total time", compute="_compute_total_overtime",
        store=True, copy=False)

    @api.depends("production_id", "production_id.product_qty",
                 "extra_time_piece", "duration")
    def _compute_total_overtime(self):
        for workorder in self:
            total_overtime = 0
            total_time = 0
            if workorder.production_id:
                total_overtime = (workorder.extra_time_piece *
                                  workorder.production_id.product_qty)
            total_time = workorder.duration + total_overtime
            workorder.total_overtime = total_overtime
            workorder.total_time = total_time
