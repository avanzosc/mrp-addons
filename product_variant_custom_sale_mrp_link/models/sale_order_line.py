# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, exceptions, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_mrp_dict(self):
        # if not self.product_id:
        #     raise exceptions.Warning(_("select a product before create a "
        #                                "manufaturing order"))
        # if self.custom_value_ids and not self.product_version_id:
        #     raise exceptions.Warning(_("select a version before create a "
        #                                "manufaturing order"))
        res = super()._action_mrp_dict()
        res['product_attribute_ids'] = [(0, 0, {
            'attribute_id': x.attribute_id.id,
            'value_id': x.value_id.id
        }) for x in self.product_attribute_ids]
        res['custom_value_ids'] = self._set_custom_lines()
        res['product_version_id'] = self.product_version_id.id
        return res

    @api.multi
    def button_copy_product_to_mrp(self):
        for sale_line in self:
            production_id = sale_line.mrp_production_id
            if production_id:
                production_id.product_tmpl_id = sale_line.product_tmpl_id
                production_id.product_id = sale_line.product_id
                sale_line.custom_value_ids.copy_to(production_id,
                                                   'custom_value_ids')
                sale_line.product_attribute_ids.copy_to(production_id,
                                                        'product_attribute_ids'
                                                        )

    def get_product_dict(self, tmpl_id, attributes):
        values = attributes.mapped("value_id.id")
        return {
            'product_tmpl_id': tmpl_id.id,
            'attribute_value_ids': [(6, 0, values)],
            'active': tmpl_id.active,
        }

    def create_product_product(self, template=None, attributes=None):
        if template and attributes:
            product_dict = self.get_product_dict(template, attributes)
            return self.env['product.product'].create(product_dict)

    @api.multi
    def _action_launch_stock_rule(self):
        for line in self:
            if not line.mrp_production_id:
                custom_value_ids = []
                for custom in line.custom_value_ids:
                    if custom.custom_value:
                        custom_value_ids.append((0, 0, {
                            'attribute_id': custom.attribute_id.id,
                            'value_id': custom.value_id.id,
                            'custom_value': custom.custom_value,
                        }))
                if not line.product_id:
                    line.product_id = line.create_product_product(line.product_tmpl_id, line.product_attribute_ids)
                super(SaleOrderLine, line.with_context(extra_fields={
                    'product_version_id': line.product_version_id.id,
                    'product_attribute_ids':
                        line.product_id.get_custom_value_lines(),
                    'custom_value_ids': custom_value_ids,
                }))._action_launch_stock_rule()
        return True
