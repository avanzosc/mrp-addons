# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line")

    def _get_po_values(self, rule):
        return {'company_id': self.company_id,
                'priority': 1,
                'warehouse_id': (self.product_id.warehouse_id or
                                 rule.warehouse_id)}

    @api.multi
    def create_automatic_purchase_order(self):
        if not self.product_id.seller_ids:
            message = _(u"There is no vendor associated to the product {}. "
                        "Please define a vendor for this product.").format(
                self.product_id.name)
            raise ValidationError(message)
        location = (self.product_id.location_id or
                    self.env.ref('stock.stock_location_stock'))
        rule = self.env['procurement.group']._get_rule(
            self.product_id, location, {})
        values = self._get_po_values(rule)
        rule.create_merge_purchase_line(self.product_id, self.product_uom_qty,
                                        self.product_uom, location,
                                        self.product_id.name,
                                        self.order_id.name, self, values)
