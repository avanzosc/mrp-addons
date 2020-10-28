# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# Copyright 2019 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from itertools import groupby
from operator import attrgetter


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_id = fields.Many2one(required=False)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product', related=False)
    attribute_value_ids = fields.Many2many(
        domain="[('id', 'in', possible_value_ids)]")
    possible_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_compute_possible_attribute_values')
    product_uom_category = fields.Many2one(
        comodel_name='uom.categ', string='UoM category',
        compute="_compute_product_category")
    product_uom = fields.Many2one(
        domain="[('category_id', '=', product_uom_category)]")

    @api.depends('product_id', 'product_tmpl_id')
    def _compute_product_category(self):
        for line in self:
            line.product_uom_category = (
                line.product_id.uom_id.category_id.id or
                line.product_tmpl_id.uom_id.category_id.id)

    @api.depends('bom_id.product_tmpl_id',
                 'bom_id.product_tmpl_id.attribute_line_ids')
    def _compute_possible_attribute_values(self):
        for line in self:
            attr_values = self.env['product.attribute.value']
            for attr_line in line.bom_id.product_tmpl_id.attribute_line_ids:
                attr_values |= attr_line.value_ids
            line.possible_value_ids = attr_values.sorted()

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(MrpBomLine, self).onchange_product_id()
        if self.product_id:
            self.product_tmpl_id = self.product_id.product_tmpl_id.id
        return res

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.product_uom = (self.product_id.uom_id.id or
                                self.product_tmpl_id.uom_id.id)
            return {'domain': {'product_id': [('product_tmpl_id', '=',
                                               self.product_tmpl_id.id)]}}
        return {'domain': {'product_id': []}}

    def _skip_bom_line(self, product):
        if self.attribute_value_ids:
            production_attr_values = []
            if not product and self.env.context.get('production'):
                production = self.env.context['production']
                for attr_value in production.product_attribute_ids:
                    production_attr_values.append(attr_value.value_id.id)
                if not self._check_product_suitable(
                        production_attr_values,
                        self.attribute_value_ids):
                    return True
            elif not product or not self._check_product_suitable(
                    product.attribute_value_ids.ids,
                    self.attribute_value_ids):
                return True
        return False

    def _check_product_suitable(self, check_attribs, component_attribs):
        """ Check if component is suitable for given attributes
        @param check_attribs: Attribute id list
        @param component_attribs: Component defined attributes to check
        @return: Component validity
        """
        getattr = attrgetter('attribute_id')
        for key, group in groupby(component_attribs, getattr):
            if not set(check_attribs).intersection([x.id for x in group]):
                return False
        return True


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    @api.model
    def _bom_find_prepare(self, product_tmpl=None, product=None,
                          picking_type=None, company_id=False):
        if not product:
            tmpl_id = product.product_tmpl_id
            active_model = self.env.context.get('params').get('model')
            # if not bom_line.type != "phantom":
            production = self.env.context.get('production')
            if not production and active_model == 'mrp.production':
                production = self.env['mrp.production'].browse(
                    self.env.context.get('params').get('id'))
            product_attribute_ids = (
                tmpl_id._get_product_attribute_ids_inherit_dict(
                    production.product_attribute_ids))
            comp_product = self.env['product.product']._product_find(
                tmpl_id, product_attribute_ids)
            if not comp_product:
                return self.env['mrp.bom']
            return self._bom_find(product=comp_product)
        return super(MrpBom, self)._bom_find_prepare(
            product_tmpl=product_tmpl, product=product,
            picking_type=picking_type, company_id=company_id)

    def _get_inherited_custom_values(self, attribute_line_ids,
                                     custom_value_ids):
        custom_values = []
        for custom_line in custom_value_ids:
            for attr in attribute_line_ids:
                if custom_line.attribute_id.id == attr['attribute_id'] and \
                        custom_line.value_id.id == attr.get('value_id'):
                    attr['custom_value'] = custom_line.custom_value
                    custom_values.append(attr)
        return custom_values

    @api.model
    def _prepare_consume_line(self, bom_line, quantity, product,
                              original_qty, parent_line):
        res_line, res = super(MrpBom, self)._prepare_consume_line(
            bom_line, quantity, product, original_qty, parent_line)
        production = self.env.context.get('production')
        active_model = self.env.context.get('params').get('model')
        if not production and active_model == 'mrp.production':
            production = self.env['mrp.production'].browse(
                self.env.context.get('params').get('id'))
        if not production:
            production = self.env['mrp.production']
        tmpl_id = bom_line.product_tmpl_id
        if not bom_line.product_id:
            res['name'] = tmpl_id.name
            res['product_tmpl_id'] = tmpl_id.id
            product_attribute_ids = (
                tmpl_id._get_product_attribute_ids_inherit_dict(
                    production.product_attribute_ids))
            comp_product = self.env['product.product']._product_find(
                tmpl_id, product_attribute_ids)
            res['product_id'] = comp_product and comp_product.id
        else:
            res['product_tmpl_id'] = bom_line.product_id.product_tmpl_id.id
            product_attribute_ids = (
                bom_line.product_id._get_product_attributes_values_dict())
        product_custom_value_ids = self._get_inherited_custom_values(
            product_attribute_ids, production.custom_value_ids)
        res['product_attribute_ids'] = list(map(
            lambda x: (0, 0, x), product_attribute_ids))
        res['custom_value_ids'] = list(map(
            lambda x: (0, 0, x), product_custom_value_ids))
        for val in res['product_attribute_ids']:
            val = val[2]
            val['product_tmpl_id'] = res['product_tmpl_id']
        return res_line, res

    @api.model
    def _get_bom_product_name(self, bom_line):
        if not bom_line.product_id:
            return bom_line.product_tmpl_id.name_get()[0][1]
        else:
            return super(MrpBom, self)._get_bom_product_name(bom_line)


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    name = fields.Char(required=False)
    product_id = fields.Many2one(required=False)
    product_tmpl_id = fields.Many2one(comodel_name="product.template",
                                      String="Product", required=True)