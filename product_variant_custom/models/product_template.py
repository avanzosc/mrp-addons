# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def _get_product_attributes_dict(self):
        if not self:
            return []
        self.ensure_one()
        return self.attribute_line_ids.mapped(
            lambda x: {'attribute_id': x.attribute_id.id})
