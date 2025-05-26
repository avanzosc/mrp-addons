# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    plates_manufactured = fields.Integer(
        compute="_compute_plates_manufactured",
        store=True,
    )

    @api.depends("time_ids.manufactured_plate")
    def _compute_plates_manufactured(self):
        for order in self:
            order.plates_manufactured = sum(order.time_ids.mapped("manufactured_plate"))
