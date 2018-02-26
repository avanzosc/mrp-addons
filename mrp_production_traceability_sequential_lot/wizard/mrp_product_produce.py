# -*- coding: utf-8 -*-
# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    def default_lot_id(self):
        res = super(MrpProductProduce, self).default_lot_id()
        if self.env.context.get('active_model') == 'mrp.production' and len(
                self.env.context.get('active_ids')) == 1:
            production = self.env['mrp.production'].browse(
                self.env.context.get('active_id'))
            if (production.unitary_production or
                    production.bom_id.unitary_production or
                    production.routing_id.unitary_production):
                return False
        return res

    lot_id = fields.Many2one(default=default_lot_id)
