# Copyright 2024 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    waiting_duration = fields.Float(
        string="Waiting", compute="_compute_waiting_duration", store=True
    )
    total_duration = fields.Float(compute="_compute_total_duration", store=True)

    @api.depends("duration", "waiting_duration")
    def _compute_total_duration(self):
        for workorder in self:
            workorder.total_duration = workorder.duration + workorder.waiting_duration

    @api.depends("date_start", "date_finished", "duration")
    def _compute_waiting_duration(self):
        for workorder in self:
            waiting = 0
            if workorder.date_start and workorder.date_finished:
                dif = workorder.date_finished - workorder.date_start
                dif = dif.total_seconds() / timedelta(minutes=1).total_seconds()
                waiting = dif - workorder.duration
            workorder.waiting_duration = waiting
