# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    plates_manufactured = fields.Integer(
        string="Plates Manufactured",
        compute="_compute_plates_manufactured",
        store=True)

    @api.depends("time_ids", "time_ids.manufactured_plate")
    def _compute_plates_manufactured(self):
        for line in self:
            line.plates_manufactured = sum(
                line.time_ids.mapped("manufactured_plate"))
