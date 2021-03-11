# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        res = super()._prepare_mo_vals(product_id, product_qty, product_uom,
                                       location_id, name, origin, values, bom)
        extra_fields = self.env.context.get('extra_fields')
        if extra_fields:
            res['product_tmpl_id'] = extra_fields.get('product_tmpl_id')
            res['product_version_id'] = extra_fields.get('product_version_id')
            res['product_attribute_ids'] = extra_fields.get(
                'product_attribute_ids')
            res['custom_value_ids'] = extra_fields.get('custom_value_ids')
        return res
