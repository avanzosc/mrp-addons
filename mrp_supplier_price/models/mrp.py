# Copyright 2016 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    supplier_id = fields.Many2one(
        comodel_name='res.partner', string='Supplier')
    supplier_id_domain = fields.Many2many(
        comodel_name='res.partner', compute='_compute_variant_suppliers',
        string='Suppliers Domain')
    standard_price = fields.Monetary(
        string='Cost', digits=dp.get_precision('Product Price'),
        compute='_compute_standard_price')
    supplier_price = fields.Monetary(
        string='Supplier Price', digits=dp.get_precision('Product Price'))
    unit_final_cost = fields.Monetary(
        string='Final Unit Cost', compute='_compute_subtotal',
        digits=dp.get_precision('Product Price'),
        help='Cost by final product unit.')
    subtotal = fields.Monetary(
        string='Subtotal', compute='_compute_subtotal',
        digits=dp.get_precision('Product Price'))
    unit_final_purchase = fields.Monetary(
        string='Final Unit Purchase Cost',
        compute='_compute_supplier_subtotal',
        digits=dp.get_precision('Product Price'),
        help='Cost by final product unit.')
    supplier_subtotal = fields.Monetary(
        string='Purchase Subtotal', compute='_compute_supplier_subtotal',
        digits=dp.get_precision('Product Price'))
    product_uop_id = fields.Many2one(
        string='Product UoP', comodel_name='uom.uom',
        compute='_compute_product_uop')
    product_uop_qty = fields.Float(
        string='Product UoP Quantity', compute='_compute_product_uop',
        digits=dp.get_precision('Product Unit of Measure'))
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        related='production_id.currency_id')

    def _select_best_cost_price(self, supplier_id=None):
        best_price = {}
        if supplier_id:
            supplier_ids = (
                self.product_id.product_tmpl_id.variant_seller_ids.filtered(
                    lambda x: x.name == supplier_id))
        else:
            supplier_ids = self.product_id.product_tmpl_id.variant_seller_ids
        for line in supplier_ids.filtered(
                lambda l: l.min_qty <= self.product_qty):
            price_unit = line.price
            if (price_unit and self.production_id.currency_id and
                    line.currency_id != self.production_id.currency_id):
                price_unit = line.currency_id.compute(
                    price_unit, self.production_id.currency_id)
            if self.product_uop_id and line.product_uom != self.product_uop_id:
                price_unit = line.product_uom._compute_price(
                    price_unit, self.product_uop_id)
            if not best_price or line.min_qty <= \
                    self.product_qty and \
                    best_price['cost'] > price_unit:
                best_price = {
                    'supplier_id': line.name.id,
                    'cost': price_unit,
                }
        return best_price

    @api.depends('product_id', 'product_id.product_tmpl_id.variant_seller_ids',
                 'product_id.product_tmpl_id.variant_seller_ids.name')
    def _compute_variant_suppliers(self):
        for line in self.filtered('product_id'):
            line.supplier_id_domain = line.product_id.mapped(
                'variant_seller_ids.name')

    @api.depends('product_id', 'product_id.standard_price')
    def _compute_standard_price(self):
        for line in self.filtered('product_id'):
            price_unit = line.product_id.standard_price
            if (price_unit and line.production_id.currency_id and
                    line.product_id.currency_id !=
                    line.production_id.currency_id):
                price_unit = line.product_id.currency_id.compute(
                    price_unit, line.production_id.currency_id)
            if (line.product_uom_id and
                    line.product_id.uom_id != line.product_uom_id):
                price_unit = line.product_id.uom_id._compute_price(
                    price_unit, line.product_uom_id)
            line.standard_price = price_unit

    @api.depends('product_id', 'product_qty')
    def _compute_product_uop(self):
        for line in self.filtered('product_id'):
            line.product_uop_id = line.product_id.uom_po_id.id
            line.product_uop_qty = line.product_uom_id._compute_quantity(
                line.product_qty, line.product_uop_id)

    @api.depends('standard_price', 'product_qty', 'production_id',
                 'production_id.product_qty')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.product_qty * line.standard_price
            line.unit_final_cost = (
                line.subtotal / (line.production_id.product_qty or 1.0))

    @api.depends('supplier_price', 'product_uop_qty', 'production_id',
                 'production_id.product_qty')
    def _compute_supplier_subtotal(self):
        for line in self:
            line.supplier_subtotal = line.product_uop_qty * line.supplier_price
            line.unit_final_purchase = (
                line.supplier_subtotal / (line.production_id.product_qty or
                                          1.0))

    @api.onchange('product_tmpl_id', 'product_id', 'product_qty')
    def onchange_product_product_qty(self):
        for line in self:
            best_supplier = line._select_best_cost_price()
            if best_supplier:
                line.supplier_id = best_supplier['supplier_id']
                line.supplier_price = best_supplier['cost']
            else:
                line.supplier_price = line.product_id.standard_price

    @api.onchange('supplier_id')
    def onchange_supplier_id(self):
        for line in self:
            best_price = line._select_best_cost_price(
                supplier_id=line.supplier_id)
            if best_price:
                line.supplier_price = best_price['cost']


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    scheduled_total = fields.Float(
        string='Total', compute='_compute_scheduled_total',
        digits=dp.get_precision('Product Price'))
    production_total = fields.Float(
        string='Production Total', compute='_compute_production_total',
        digits=dp.get_precision('Product Price'))
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)

    @api.depends('product_line_ids', 'product_line_ids.supplier_subtotal')
    def _compute_scheduled_total(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        by_unit = get_param('mrp.subtotal_by_unit') == 'True'
        for mrp in self.filtered(lambda m: m.product_line_ids):
            subtotal = sum(mrp.mapped('product_line_ids.supplier_subtotal'))
            mrp.scheduled_total = (
                subtotal / (mrp.product_qty or 1.0) if by_unit else subtotal)

    @api.depends('scheduled_total')
    def _compute_production_total(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        by_unit = get_param('mrp.subtotal_by_unit') == 'True'
        for prod in self:
            total = prod.scheduled_total
            try:
                total += prod.routing_total
            except Exception:
                pass
            prod.production_total =\
                total * (prod.product_qty if by_unit else 1)

    @api.multi
    def button_recompute_total(self):
        fields_list = ["scheduled_total", 'production_total']
        for field in fields_list:
            self.env.add_todo(self._fields[field], self)
        self.recompute()

    @api.multi
    def _action_compute_lines(self):
        res = super(MrpProduction, self)._action_compute_lines()
        for line in self.product_line_ids:
            line.onchange_product_product_qty()
        return res
