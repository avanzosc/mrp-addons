# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _
from odoo.addons import decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    dimension = fields.Float(string="Product Dimension",
                             related="product_id.dimension",
                             digits=dp.get_precision('Dimension'))
    weight = fields.Float(string="Product Weight",
                          related="product_id.product_base_weight",
                          digits=dp.get_precision('Dimension'))
    version_dimension = fields.Float(string="Product Dimension",
                                     digits=dp.get_precision('Dimension'))
    version_weight = fields.Float(string="Product Weight",
                                  digits=dp.get_precision('Dimension'))
    total_dimension = fields.Float(string="Total Dimension",
                                   digits=dp.get_precision('Dimension'))
    total_weight = fields.Float(string="Total Weight",
                                digits=dp.get_precision('Dimension'))

    @api.onchange("product_qty", "custom_value_ids")
    def _compute_total_dimension_weight(self):
        for line in self:
            multiplication = 1
            dimensions_attr = \
                list(line.product_id.product_tmpl_id.attribute_dimensions._ids)
            dimension_attributes_qty = len(dimensions_attr)
            dimension_values_qty = 0
            if not dimensions_attr:
                return
            for attr in line.custom_value_ids:
                if attr.attribute_id.id in dimensions_attr:
                    dimension_values_qty += 1
                    try:
                        multiplication *= float(attr.custom_value)
                        dimensions_attr.remove(attr.attribute_id.id)
                    except ValueError:
                        raise exceptions.UserError(
                            _("Cant convert custom value to number"
                              "in attribute: %s") % attr.attribute_id.name)
            for value in line.product_id.attribute_value_ids:
                if value.attribute_id.id in dimensions_attr:
                    dimension_values_qty += 1
                    try:
                        multiplication *= float(value.name)
                    except ValueError:
                        raise exceptions.UserError(
                            _("Cant convert custom value to number"
                              "in attribute: %s") % value.attribute_id.name)
            if dimension_attributes_qty == dimension_values_qty:
                weight = line.product_id.product_tmpl_id.base_weight
                line.version_dimension = multiplication
                line.version_weight = multiplication * weight
                line.total_dimension = multiplication * line.product_qty
                line.total_weight = multiplication * weight * line.product_qty

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'version_dimension',
                 'version_weight', 'custom_value_ids')
    def _compute_amount(self):
        super()._compute_amount()
        for line in self:
            price_by = line.product_id.product_tmpl_id.price_by
            if price_by == 'qty':
                continue
            if price_by == 'dimension':
                dimension = line.version_dimension
                line.update({
                    'price_tax': line['price_tax'] * dimension,
                    'price_total': line['price_total'] * dimension,
                    'price_subtotal': line['price_subtotal'] * dimension,
                })
            else:
                weight = line.version_weight
                line.update({
                    'price_tax': line['price_tax'] * weight,
                    'price_total': line['price_total'] * weight,
                    'price_subtotal': line['price_subtotal'] * weight,
                })
