# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# Copyright 2019 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _get_product_attributes_dict(self):
        if not self:
            return []
        self.ensure_one()
        return self.attribute_line_ids.mapped(
            lambda x: {'attribute_id': x.attribute_id.id})

    def _get_product_attribute_ids_inherit_dict(self, product_attribute_list):
        product_attribute_ids = self._get_product_attributes_dict()
        for attr in product_attribute_ids:
            if self.env['product.attribute'].browse(
                    attr['attribute_id']).parent_inherited:
                for attr_line in product_attribute_list:
                    if attr_line.attribute_id.id == attr['attribute_id']:
                        attr.update({'value_id': attr_line.value_id.id})
                        try:
                            attr.update({'custom_value':
                                         attr_line.custom_value})
                        except Exception:
                            pass
        return product_attribute_ids
