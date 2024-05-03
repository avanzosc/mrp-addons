# -*- coding: utf-8 -*-
# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    @api.depends('picking_id', 'picking_id.picking_type_id',
                 'product_id', 'product_id.product_tmpl_id',
                 'product_id.product_tmpl_id.brand_ids',
                 'product_id.product_tmpl_id.brand_ids.partner_id',
                 'product_id.product_tmpl_id.brand_ids.code')
    def _compute_product_brand_code(self):
        for move in self:
            my_brand_code = ''
            my_brand_supplier = ''
            if move.product_id:
                brands = move.product_id.product_tmpl_id.mapped(
                    'brand_ids').filtered(lambda x: x.code)
                for brand in brands:
                    my_brand_code = (
                        brand.code if not my_brand_code else
                        u"{}, {}".format(my_brand_code, brand.code))
                    if brand.partner_id:
                        my_brand_supplier = (
                            brand.partner_id.name if not my_brand_supplier else
                            u"{}, {}".format(my_brand_supplier,
                                             brand.partner_id.name))
            if my_brand_code != move.product_brand_code:
                move.product_brand_code = my_brand_code
            if my_brand_supplier != move.brand_supplier:
                move.brand_supplier = my_brand_supplier

    product_brand_code = fields.Char(
        string='Product brand code', compute='_compute_product_brand_code',
        store=True)
    brand_supplier = fields.Char(
        string='Fabricator', store=True,
        compute='_compute_product_brand_code')

    @api.model
    def run_scheduler_stock_move_brand_supplier(self):
        cond = []
        lines = self.env['stock.move'].search(cond)
        for line in lines:
            try:
                my_brand_supplier = ''
                if line.product_id:
                    brands = line.product_id.product_tmpl_id.mapped(
                        'brand_ids').filtered(lambda x: x.code)
                    for brand in brands:
                        if brand.partner_id:
                            my_brand_supplier = (
                                brand.partner_id.name if not my_brand_supplier else
                                u"{}, {}".format(my_brand_supplier,
                                                 brand.partner_id.name))
                if my_brand_supplier:
                    self.env.cr.execute('update stock_move set brand_supplier=%s where id=%s', (my_brand_supplier, line.id))
            except Exception:
                pass
