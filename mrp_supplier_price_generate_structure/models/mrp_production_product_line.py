# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    def _get_po_values(self, rule):
        res = super()._get_po_values(rule)
        res.update({'partner_id': self.supplier_id.id})
        return res

    def create_automatic_purchase_order(self, origin_manufacture_order, level):
        if self.supplier_id not in self.product_id.seller_ids.mapped(
                'name'):
            self.env['product.supplierinfo'].create({
                'name': self.supplier_id.id,
                'product_tmpl_id': self.product_id.product_tmpl_id.id,
            })
        return super().create_automatic_purchase_order(
            origin_manufacture_order, level)
