# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpProductionProductLine(models.Model):
    _inherit = "mrp.production.product.line"

    @api.multi
    def create_automatic_manufacturing_order(self, origin_manufacture_order,
                                             analytic_account):
        custom_value_ids = []
        for custom in self.custom_value_ids:
            if custom.custom_value:
                custom_value_ids.append((0, 0, {
                    'attribute_id': custom.attribute_id.id,
                    'value_id': custom.value_id.id,
                    'custom_value': custom.custom_value,
                }))
        return super(MrpProductionProductLine, self.with_context(extra_fields={
            'product_tmpl_id': self.product_tmpl_id.id,
            'product_version_id': self.product_version_id.id,
            'product_attribute_ids': [(0, 0, {
                'attribute_id': x.attribute_id.id,
                'value_id': x.value_id.id
            }) for x in self.product_attribute_ids],
            'custom_value_ids': custom_value_ids,
        })).create_automatic_manufacturing_order(
            origin_manufacture_order, analytic_account)
