# Copyright 2020 Alfredo de la Fuente - Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po, partner):
        values = super(StockRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner)
        if 'analytic_account_id' in self.env.context and self.env.context.get(
                'analytic_account_id', False):
            values['account_analytic_id'] = self.env.context.get(
                'analytic_account_id').id
        return values
