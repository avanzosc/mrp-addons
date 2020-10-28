# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_approve(self, force=False):
        for line in self.order_line:
            product_version = line.product_id._find_version(
                line.custom_value_ids)
            if product_version:
                line.product_version_id = product_version
            else:
                custom_value_ids = []
                name = ""
                for custom in line.custom_value_ids:
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
                product_version = self.env["product.version"].create({
                    'product_id': line.product_id.id,
                    'name': name,
                    'custom_value_ids': custom_value_ids,
                })
                line.product_version_id = product_version
        return super().button_approve()


class PurchaseOrder(models.Model):
    _inherit = "purchase.order.line"

    product_tmpl_id = fields.Many2one(comodel_name="product.template")
    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Product Version")
    product_attribute_ids = fields.One2many(
        comodel_name='purchase.line.attribute',
        inverse_name='purchase_line_id',
        string='Product attributes', copy=True, readonly=True,
        states={'draft': [('readonly', False)]},)
    version_value_ids = fields.One2many(
        comodel_name="product.version.line",
        related="product_version_id.custom_value_ids")
    custom_value_ids = fields.One2many(
        comodel_name="purchase.version.custom.line", string="Custom Values",
        inverse_name="line_id", copy=True)

    def _delete_product_attribute_ids(self):
        delete_values = []
        for value in self.product_attribute_ids:
            delete_values.append((2, value.id))
        return delete_values

    def _delete_custom_lines(self):
        delete_values = []
        for value in self.custom_value_ids:
            delete_values.append((2, value.id))
        return delete_values

    def _set_custom_lines(self):
        if self.product_version_id:
            return self.product_version_id.get_custom_value_lines()
        elif self.product_id:
            return self.product_id.get_custom_value_lines()

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_template(self):
        self.ensure_one()
        self.product_attribute_ids = \
            self._delete_product_attribute_ids()
        self.custom_value_ids = self._delete_custom_lines()
        if self.product_tmpl_id:
            self.product_uom = self.product_tmpl_id.uom_id
            if (not self.product_tmpl_id.attribute_line_ids and
                    not self.product_id):
                self.product_id = (
                        self.product_tmpl_id.product_variant_ids and
                        self.product_tmpl_id.product_variant_ids[0])
                self.product_attribute_ids = (
                    self.product_id._get_product_attributes_values_dict())
            self.product_attribute_ids = (
                self.product_tmpl_id._get_product_attributes_dict())
            return {'domain': {'product_id':
                                   [('product_tmpl_id', '=',
                                     self.product_tmpl_id.id)]}}
        return {'domain': {}}

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super().onchange_product_id()
        self.custom_value_ids = self._delete_custom_lines()
        self.product_attribute_ids = self._delete_product_attribute_ids()
        if self.product_id:
            product = self.product_id
            self.product_attribute_ids = \
                product._get_product_attributes_values_dict()

            self.custom_value_ids = self._set_custom_lines()
            version = self.product_id._find_version(self.custom_value_ids)
            self.product_version_id = version
        return result

    @api.onchange('product_attribute_ids')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        product_tmpl_id = self.product_tmpl_id
        self.product_id = product_obj._product_find(self.product_tmpl_id,
                                                    self.product_attribute_ids)
        self.product_tmpl_id = product_tmpl_id

    def _get_purchase_line_description(self):
        if not self.product_id:
            return
        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name or ""
        version_description = " "
        for value_line in self.custom_value_ids:
            if value_line.custom_value:
                version_description += "[{}: {}({})]".format(
                    value_line.attribute_id.name, value_line.value_id.name,
                    value_line.custom_value)
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase
        return self.name + version_description

    @api.onchange('product_version_id')
    def product_version_id_change(self):
        if self.product_version_id:
            self.product_id = self.product_version_id.product_id
            self.name = self._get_purchase_line_description()
        self.custom_value_ids = self._delete_custom_lines()
        self.custom_value_ids = self._set_custom_lines()

    @api.onchange('custom_value_ids')
    def onchange_version_lines(self):
        product_version = self.product_id._find_version(
            self.custom_value_ids)
        self.product_version_id = product_version
        self.name = self._get_purchase_line_description()


class PurchaseLineAttribute(models.Model):
    _inherit = "product.attribute.line"
    _name = 'purchase.line.attribute'

    product_tmpl_id = fields.Many2one(
        related='purchase_line_id.product_tmpl_id')
    purchase_line_id = fields.Many2one(comodel_name='purchase.order.line',
                                       string='Purchase Order Line')


class PurchaseVersionCustomLine(models.Model):
    _inherit = "version.custom.line"
    _name = "purchase.version.custom.line"

    line_id = fields.Many2one(comodel_name="purchase.order.line")
