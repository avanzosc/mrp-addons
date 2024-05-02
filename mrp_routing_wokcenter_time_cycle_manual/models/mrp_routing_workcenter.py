# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    number_insertions = fields.Integer(
        string="Number of insertions",
        default=0,
        copy=False,
    )
    insertion_time = fields.Float(
        string="Insertion time",
        default=0,
        copy=False,
    )

    @api.onchange("number_insertions", "insertion_time")
    def onchange_insertion_number_time(self):
        time_cycle_manual = 0
        if self.number_insertions and self.insertion_time:
            time_cycle_manual = self.number_insertions * self.insertion_time
        self.time_cycle_manual = time_cycle_manual
