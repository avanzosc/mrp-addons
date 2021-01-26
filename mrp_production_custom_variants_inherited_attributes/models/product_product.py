# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# Copyright 2019 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _get_product_custom_values_dict(self, custom_value_ids):
        attrs = self.product_tmpl_id._get_product_attributes_dict()
        res = []
        for val in attrs:
            value = self.attribute_value_ids.filtered(
                lambda x: x.attribute_id.id == val['attribute_id'])
            if value.is_custom:
                val['value_id'] = value.id
                res.append(val)
        return res

    @api.model
    def _build_attributes_domain(self, product_template, product_attributes):
        domain = []
        cont = 0
        if product_template:
            domain.append(('product_tmpl_id', '=', product_template.id))
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    value_id = attr_line.get('value_id')
                else:
                    value_id = attr_line.value_id.id
                if value_id:
                    domain.append(('attribute_value_ids', '=', value_id))
                    cont += 1
        return domain, cont
