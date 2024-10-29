# Copyright 2024 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    timesheet_id = fields.Many2one(
        string="Timesheet",
        comodel_name="account.analytic.line",
    )
