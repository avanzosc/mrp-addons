# -*- coding: utf-8 -*-
# Copyright 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    unitary_production = fields.Boolean(string='Unitary Production')

    @api.model
    def default_get(self, fields_list):
        res = super(MrpProductProduce, self).default_get(fields_list)
        if self.env.context.get('active_model') == 'mrp.production' and len(
                self.env.context.get('active_ids')) == 1:
            production = self.env['mrp.production'].browse(
                self.env.context.get('active_id'))
            res.update({
                'unitary_production':
                    production.unitary_production or
                    production.bom_id.unitary_production or
                    production.routing_id.unitary_production,
            })
        return res

    @api.onchange('unitary_production')
    def _onchange_unitary_production(self):
        self.ensure_one()
        if self.unitary_production:
            self.product_qty = 1.0
