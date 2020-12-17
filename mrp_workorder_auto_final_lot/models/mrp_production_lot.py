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
    wo_produce_move_line_ids = fields.One2many(
        comodel_name="stock.move.line", compute="_compute_lot_moves",
        string="Produced Lines")
    wo_consume_move_line_ids = fields.One2many(
        comodel_name="stock.move.line", compute="_compute_lot_moves",
        string="Consumed Lines")

    def _compute_lot_moves(self):
        for lot in self:
            workorder_id = self._context.get('moves_workorder_id', False)
            if workorder_id:
                workorder_id = self._context.get('active_id', False)
                workorder_moves = self.env['stock.move.line'].search([(
                    'workorder_id', '=', workorder_id)])
                lot.wo_produce_move_line_ids = \
                    lot.produce_move_line_ids.filtered(
                        lambda x: x.id in workorder_moves.ids)
                lot.wo_consume_move_line_ids = \
                    lot.consume_move_line_ids.filtered(
                        lambda x: x.id in workorder_moves.ids)
