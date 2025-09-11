# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    initial_plate = fields.Integer()
    final_plate = fields.Integer()
    manufactured_plate = fields.Integer(
        compute="_compute_manufactured_plate",
        store=True,
    )
    speed_average = fields.Float(
        compute="_compute_speed_average",
        store=True,
    )

    @api.depends("initial_plate", "final_plate")
    def _compute_manufactured_plate(self):
        for line in self:
            line.manufactured_plate = line.final_plate - line.initial_plate

    @api.depends("manufactured_plate", "duration")
    def _compute_speed_average(self):
        for line in self:
            line.speed_average = 0
            if line.duration != 0:
                line.speed_average = line.manufactured_plate / line.duration

    @api.constrains("manufactured_plate")
    def _check_manufactured_plate(self):
        for line in self:
            if line.manufactured_plate < 0:
                raise ValidationError(
                    _("Error: Manufactured plates should be positive.")
                )
