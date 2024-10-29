# Copyright 2024 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    timesheet_ids = fields.One2many(
        string="Timesheet",
        comodel_name="account.analytic.line",
        inverse_name="mrp_production_id",
    )
