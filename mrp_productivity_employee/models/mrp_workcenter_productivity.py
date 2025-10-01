# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    employee_id = fields.Many2one(
        string="Employee", comodel_name="hr.employee", copy=False
    )

    @api.constrains("workorder_id")
    def _check_open_time_ids(self):
        if "from_wizard_button_start" not in self.env.context:
            return super()._check_open_time_ids()
        else:
            return True
