# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sale_line_ids = fields.One2many(comodel_name="sale.order.line",
                                    inverse_name="purchase_order_line_id")
    mrp_production_product_line_ids = fields.One2many(
        comodel_name="mrp.production.product.line",
        inverse_name="purchase_order_line_id")
    sale_qty = fields.Float(compute="_compute_total_qty")
    mrp_qty = fields.Float(compute="_compute_total_qty")
    total_qty = fields.Float(compute="_compute_total_qty")
    extra_qty = fields.Float("Product Quantity")

    @api.depends("sale_line_ids", "mrp_production_product_line_ids")
    def _compute_total_qty(self):
        self.sale_qty = sum(self.sale_line_ids.mapped("product_qty"))
        self.mrp_qty = sum(
            self.mrp_production_product_line_ids.mapped("product_qty"))
        self.total_qty = self.sale_qty + self.mrp_qty

    @api.onchange("total_qty", "extra_qty")
    def onchange_lines_qty(self):
        self.product_qty = self.total_qty + self.extra_qty
