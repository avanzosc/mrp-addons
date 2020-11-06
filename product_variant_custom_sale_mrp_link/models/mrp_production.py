# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_copy_product_to_sale_line(self):
        for mo in self:
            sale_line_id = mo.sale_line_id
            if sale_line_id:
                sale_line_id.product_tmpl_id = mo.product_tmpl_id
                sale_line_id.product_id = mo.product_id
                mo.custom_value_ids.copy_to(sale_line_id,
                                            'custom_value_ids')
                mo.product_attribute_ids.copy_to(sale_line_id,
                                                 'product_attribute_ids')
