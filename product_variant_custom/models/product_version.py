# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class ProductVersion(models.Model):
    _name = "product.version"
    _description = "Product Version"

    name = fields.Char(string="Name")
    product_tmpl_id = fields.Many2one(related="product_id.product_tmpl_id")
    product_id = fields.Many2one(comodel_name="product.product",
                                 string="Product")
    custom_value_ids = fields.One2many(comodel_name="product.version.line",
                                       inverse_name="product_version_id",
                                       string="Custom Values")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")

    @api.multi
    def get_custom_value_lines(self):
        self.ensure_one()
        lines = []
        values = self.custom_value_ids
        for value in values:
            lines.append(
                (0, 0, {
                    'attribute_id': value.attribute_id.id,
                    'value_id': value.value_id.id,
                    'custom_value': value.custom_value,
                }))
        return lines

    @api.multi
    def get_version_dict(self, product_id, custom_lines):
        name = ""
        custom_value_ids = []
        for custom in custom_lines:
            if custom.custom_value:
                custom_value_ids.append((0, 0, {
                    'attribute_id': custom.attribute_id.id,
                    'value_id': custom.value_id.id,
                    'custom_value': custom.custom_value,
                }))
                if name:
                    name = "{}, ({}):{}".format(
                        name, custom.value_id.name, custom.custom_value
                    )
                else:
                    name = "({}):{}".format(
                        custom.value_id.name, custom.custom_value)
        return {
            'product_id': product_id,
            'name': name,
            'custom_value_ids': custom_value_ids,
        }

    def _create_version(self, product_id, custom_values):
        product_version = False
        if product_id and custom_values.filtered(lambda x: x.custom_value):
            version_values = self.get_version_dict(product_id, custom_values)
            product_version = self.env["product.version"].create(
                version_values)
        return product_version

    def _find_version(self, product_id, custom_values):
        product = self.env['product.product'].browse(product_id)
        return product._find_version(custom_values)

    def _find_create_version(self, product_id, custom_values):
        version = self._find_version(product_id, custom_values)
        if not version:
            version = self._create_version(product_id, custom_values)
        return version


class ProductVersionLine(models.Model):
    _name = "product.version.line"
    _description = "Product Version Line"

    product_version_id = fields.Many2one(comodel_name="product.version")
    attribute_id = fields.Many2one(comodel_name="product.attribute",
                                   string="Attribute")
    value_id = fields.Many2one(comodel_name="product.attribute.value",
                               string="Value")
    custom_value = fields.Char(string="Custom value")

    @api.constrains('custom_value')
    def _check_custom_range(self):
        for line in self:
            value = line.value_id
            try:
                custom = line.custom_value
                custom_value = float(custom)
            except ValueError:
                return
            if value.min_value == value.max_value == 0:
                return
            if custom_value < value.min_value >= 0:
                raise exceptions.UserError(_(
                    "Custom value is smaller than minimum allowed for this "
                    "value"))
            if custom_value > value.max_value >= 0:
                raise exceptions.UserError(_(
                    "Custom value is greater than maximum allowed for this "
                    "value"))


class VersionCustomLine(models.AbstractModel):
    _name = "version.custom.line"
    _description = "Version Custom Line"

    attribute_id = fields.Many2one(comodel_name="product.attribute",
                                   string="Attribute")
    value_id = fields.Many2one(comodel_name="product.attribute.value",
                               string="Value")
    custom_value = fields.Char(string="Custom value")

    @api.constrains('custom_value')
    def _check_custom_range(self):
        for line in self:
            value = line.value_id
            try:
                custom = line.custom_value
                custom_value = float(custom)
            except ValueError:
                return
            if value.min_value == value.max_value == 0:
                return
            if custom_value < value.min_value >= 0:
                raise exceptions.UserError(_(
                    "Custom value is smaller than minimum allowed for this "
                    "value"))
            if custom_value > value.max_value >= 0:
                raise exceptions.UserError(_(
                    "Custom value is greater than maximum allowed for this "
                    "value"))

    @api.multi
    def copy_to(self, instance, field):
        for line in instance[field]:
            line.unlink()
        copy_fields = []
        for attribute_line in self:
            copy_fields.append((0, 0, {
                'attribute_id': attribute_line.attribute_id,
                'value_id': attribute_line.value_id,
                'custom_value': attribute_line.custom_value,
            }))
        instance[field] = copy_fields
