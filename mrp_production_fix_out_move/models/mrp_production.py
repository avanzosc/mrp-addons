# -*- coding: utf-8 -*-
# Copyright 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def action_produce(
            self, production_id, production_qty, production_mode, wiz=False):
        res = super(MrpProduction, self).action_produce(
            production_id, production_qty, production_mode, wiz=wiz)
        production = self.env['mrp.production'].browse(production_id)
        max_move = max(production.move_created_ids2, key=lambda x: x.id)
        if max_move:
            prev_moves = production.mapped('move_created_ids2').filtered(
                lambda l: l.id != max_move.id and l.move_dest_id and
                l.location_id == max_move.location_id and
                l.location_dest_id == max_move.location_dest_id and
                l.product_id == max_move.product_id)
            if prev_moves:
                self._no_duplicate_move_in_out_picking(prev_moves, max_move)
        return res

    def _no_duplicate_move_in_out_picking(self, prev_moves, max_move):
        prev_move = max(prev_moves, key=lambda x: x.id)
        prev_move.move_dest_id.sudo().write({
            'product_uom_qty': (
                prev_move.move_dest_id.product_uom_qty +
                max_move.move_dest_id.product_uom_qty),
            'product_uos_qty': (
                prev_move.move_dest_id.product_uos_qty +
                max_move.move_dest_id.product_uos_qty)})
        for quant in max_move.move_dest_id.reserved_quant_ids:
            for previus_quant in prev_move.move_dest_id.reserved_quant_ids:
                if quant.product_id == previus_quant.product_id:
                    if quant.reservation_id:
                        quant.reservation_id = prev_move.move_dest_id
                    max_move.move_dest_id.quant_ids = [(3, quant.id)]
                    prev_move.move_dest_id.quant_ids = [(4, quant.id)]
                    max_move.move_dest_id.action_cancel()
                    max_move.move_dest_id.sudo().unlink()
                    break
