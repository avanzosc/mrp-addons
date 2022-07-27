# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class KillingCost(models.Model):
    _name = "killing.cost"
    _description = "Killing Cost"

    name = fields.Char(string="Month", required=True)
    cost = fields.Float(string="Cost")
    seq = fields.Integer(string="Sequence")
