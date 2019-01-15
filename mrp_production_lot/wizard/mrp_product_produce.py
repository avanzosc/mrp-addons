# -*- coding: utf-8 -*-
# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduce, self).default_get(fields)
        context = self.env.context
        active_id = context and context.get('active_id', False) or False
        if active_id:
            production = self.env['mrp.production'].browse(active_id)
            if production.stock_production_lot_id:
                res.update({'lot_id': production.stock_production_lot_id.id})
        return res
