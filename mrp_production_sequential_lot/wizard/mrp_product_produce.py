# -*- coding: utf-8 -*-
# Copyright 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.model
    def _get_track(self):
        res = super(MrpProductProduce, self)._get_track()
        return res if not self.unitary_production else False

    @api.onchange('unitary_production')
    def _onchange_unitary_production(self):
        self.track_production = self._get_track()
        super(MrpProductProduce, self)._onchange_unitary_production()

    @api.multi
    def do_produce(self):
        if (self.track_production or self.product_id.track_all or
                self.product_id.track_production) and not self.lot_id:
            production_id = self.env.context.get('active_id', False)
            production = self.env['mrp.production'].browse(production_id)
            sequence = self.env.ref(
                'mrp_production_sequential_lot.lot_sequence')
            lot_name = self.env['ir.sequence'].next_by_id(sequence.id)
            num = len(production.move_created_ids2.filtered(
                lambda m: m.state == 'done' and
                m.location_dest_id == production.location_dest_id)) + 1
            self.lot_id = self.lot_id.create({
                'name': lot_name or u"{}-{}".format(production.name, num),
                'product_id': self.product_id.id,
            })
        return super(MrpProductProduce, self).do_produce()
