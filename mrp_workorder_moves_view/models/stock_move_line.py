# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    produce_move_line_ids = fields.One2many(
        comodel_name="stock.move.line", inverse_name='lot_id',
        string="Produced Lines")
    consume_move_line_ids = fields.One2many(
        comodel_name="stock.move.line", inverse_name='lot_produced_id',
        string="Consumed Lines")
