# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    base_weight = fields.Float(string="Base Weight", default=1,
                               digits=dp.get_precision('Dimension'))
    weight_uom = fields.Many2one(comodel_name="uom.uom", string="uom")
    attribute_dimensions = fields.Many2many(
        comodel_name="product.attribute", string="Dimensions")
    price_by = fields.Selection(string="Price by", selection=[
        ('qty', 'Quantity'),
        ('dimension', 'Dimension'),
        ('weight', 'Weight')], default='qty')


class ProductProduct(models.Model):
    _inherit = "product.product"

    dimension = fields.Float(compute="_compute_dimension", string="Dimension",
                             digits=dp.get_precision('Dimension'))
    product_base_weight = fields.Float(compute="_compute_base_weight",
                                       string="Base Weight",
                                       digits=dp.get_precision('Dimension')
                                       )
    invisible_dimension = fields.Boolean(string="invisible_dimension",
                                         compute="_compute_dimension")

    @api.depends("product_tmpl_id.attribute_dimensions")
    def _compute_dimension(self):
        for product in self:
            multiplication = 1
            dimensions_attr = product.product_tmpl_id.attribute_dimensions
            custom_attributes = product.get_custom_attributes()
            if custom_attributes:
                product.dimension = 1
                product.invisible_dimension = True
                continue
            for value in product.attribute_value_ids:
                if value.attribute_id in dimensions_attr:
                    try:
                        multiplication *= float(value.name)
                    except ValueError:
                        raise exceptions.UserError(_(
                            "Dimensionable attribute value cant be cast in "
                            "float value: %s" % value.name))
            product.dimension = multiplication
            product.invisible_dimension = False

    @api.depends("dimension", "product_tmpl_id.base_weight")
    def _compute_base_weight(self):
        for product in self:
            product.product_base_weight = product.dimension * \
                                          product.product_tmpl_id.base_weight


class ProductVersion(models.Model):
    _inherit = "product.version"

    dimension = fields.Float(compute="_compute_dimension", string="Dimension")
    product_base_weight = fields.Float(compute="_compute_base_weight",
                                       string="Base Weight")

    @api.depends("product_id.product_tmpl_id.attribute_dimensions")
    def _compute_dimension(self):
        for product in self:
            multiplication = 1
            dimensions_attr = \
                product.product_id.product_tmpl_id.attribute_dimensions
            custom_attributes = product.product_id.get_custom_attributes()
            for value in product.product_id.attribute_value_ids:
                if value.attribute_id.id in custom_attributes and \
                        value.attribute_id in dimensions_attr:
                    custom_value = product.custom_value_ids.filtered(
                        lambda x: x.value_id.id == value.id)
                    try:
                        multiplication *= float(custom_value.custom_value)
                    except ValueError:
                        raise exceptions.UserError(_(
                            "Dimensionable attribute value cant be cast in "
                            "float value: %s" % value))
                elif value.attribute_id in dimensions_attr:
                        try:
                            multiplication *= float(value.name)
                        except ValueError:
                            raise exceptions.UserError(_(
                                "Dimensionable attribute value cant be cast in "
                                "float value"))
            product.dimension = multiplication

    @api.depends("dimension", "product_id.product_tmpl_id.base_weight")
    def _compute_base_weight(self):
        for product in self:
            product.product_base_weight = product.dimension * \
                product.product_id.product_tmpl_id.base_weight
