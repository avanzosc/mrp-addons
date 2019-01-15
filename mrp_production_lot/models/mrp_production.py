# -*- coding: utf-8 -*-
# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    stock_production_lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Final lot')

    @api.multi
    def action_confirm(self):
        result = super(MrpProduction, self).action_confirm()
        for production in self:
            production.stock_production_lot_id = production._create_final_lot()
        return result

    def _create_final_lot(self):
        lot_id = self.env['stock.production.lot'].with_context(
            {'product_id': self.product_id.id}).create(
            self._prepare_final_lot_data())
        lot_id.onchange_mrp_date()
        return lot_id

    def _prepare_final_lot_data(self):
        date_planned = fields.Datetime.from_string(self.date_planned).date()
        vals = {'name': self.name,
                'production_id': self.id,
                'product_id': self.product_id.id,
                'mrp_date': date_planned}
        return vals
