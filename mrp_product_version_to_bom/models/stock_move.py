# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    version = fields.Char(
        string='Version', related='bom_line_id.version', store=True)
