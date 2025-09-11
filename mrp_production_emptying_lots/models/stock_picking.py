# Copyright 2025 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    emptying_production_id = fields.Many2one(comodel_name="mrp.production")
