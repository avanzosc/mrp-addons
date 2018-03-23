# -*- coding: utf-8 -*-
# Copyright 2018 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    sample_order = fields.Many2one(comodel_name='purchase.order',
                                   string='Purchase Order')

    @api.multi
    def is_external_laboratory_picking(self):
        self.ensure_one()
        picking_type = self.picking_type_id
        location = picking_type.default_location_dest_id
        purchase = self.sample_order
        return bool(picking_type.code == 'outgoing' and
                    location.usage == 'customer' and purchase)

    @api.multi
    def is_incoming_picking(self):
        self.ensure_one()
        picking_type = self.picking_type_id
        location = picking_type.default_location_src_id
        return bool(picking_type.code == 'incoming' and
                    location.usage == 'supplier')

    @api.model
    def _prepare_pack_ops(self, picking, quants, forced_qties):
        res = super(StockPicking, self)._prepare_pack_ops(
            picking, quants, forced_qties)
        order = picking.mapped('move_lines.purchase_line_id.order_id')
        sample_order = self.env['purchase.order'].search(
            [('origin_qcp_purchase_id', '=', order.id)])
        if order and sample_order:
            for dict in res:
                product_id = dict.get('product_id')
                if picking.move_lines.filtered(lambda x: x.restrict_lot_id and
                                               x.product_id.id == product_id):
                    lot = picking.move_lines.filtered(
                        lambda x: x.product_id.id == product_id
                        ).mapped('restrict_lot_id')
                    dict.update({'lot_id': lot.id})
        return res


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        for record in self.filtered(lambda x: x.picking_id):
            if record.picking_id.is_incoming_picking() and \
                    record.purchase_line_id.order_id.sample_order:
                lots = record.mapped('quant_ids.lot_id')
                record.propagate_lot_id(lots.id)
        return res

    @api.multi
    def propagate_lot_id(self, restrict_lot_id):
        self.ensure_one()
        origin_po = self.purchase_line_id.order_id.origin_qcp_purchase_id
        po_lines = origin_po.order_line.filtered(lambda x: x.product_id.id ==
                                                 self.product_id.id)
        po_lines.mapped('move_ids').write({'restrict_lot_id': restrict_lot_id})
