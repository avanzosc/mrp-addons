# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpBomByproduct(models.Model):
    _inherit = "mrp.bom.byproduct"

    coefficient = fields.Float(
        string="Coefficient")
    expense_kg = fields.Boolean(
        string="Production Cost",
        default=False)
    cost = fields.Float(
        string="Fixed Price")
