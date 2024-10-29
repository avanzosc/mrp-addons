# Copyright 2024 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    mrp_production_id = fields.Many2one(
        string="Production Order",
        comodel_name="mrp.production",
    )
