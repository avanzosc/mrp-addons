# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        res = super()._prepare_mo_vals(product_id, product_qty, product_uom,
                                       location_id, name, origin, values, bom)
        extra_fields = self.env.context.get('sale_line_fields')
        if extra_fields:
            res['product_tmpl_id'] = extra_fields.get('product_tmpl_id')
            res['sale_line_id'] = extra_fields.get('sale_line_id')
            res['active'] = extra_fields.get('active')
        return res
