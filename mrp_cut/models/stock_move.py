# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    long_cut = fields.Float(
        string='Long Cut (mm)', related='bom_line_id.long_cut', store=True)
    qty_pieces_set = fields.Integer(
        string='Quantity of Pieces in Set',
        related='bom_line_id.qty_pieces_set', store=True)
    qty_pieces_cut = fields.Float(
        string='Pieces to Cut', default=lambda self: self.qty_pieces_set)
