# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    production_id = fields.Many2one(string="Production", comodel_name="mrp.production")
    unload_date = fields.Datetime(
        string="Unload Date",
        related="production_id.saca_line_id.unload_date",
        store=True,
    )
