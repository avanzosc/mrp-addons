# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class MrpProductionProductLine(models.Model):
    _inherit = "mrp.production.product.line"

    profit_percent = fields.Float(
        string="Profit Percentage", related="production_id.profit_percent")
    commercial_percent = fields.Float(
        string="Commercial Percentage",
        related="production_id.commercial_percent")
    external_commercial_percent = fields.Float(
        string="External Commercial Percentage",
        related="production_id.external_commercial_percent")

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale line",
        related="production_id.sale_line_id",
        store=True)
    order_id = fields.Many2one(comodel_name="sale.order",
                               related="sale_line_id.order_id", store=True)
    # bom_products = fields.Many2many(comodel_name="product.product",
    #                                 compute="_compute_bom_products")
    profit = fields.Float(
        string="Profit", digits=dp.get_precision("Product Price"))
    commercial = fields.Float(
        string="Commercial", digits=dp.get_precision("Product Price"))
    external_commercial = fields.Float(
        string="External", digits=dp.get_precision("Product Price"))
    price = fields.Float(
        string="Price", compute="_compute_profit",
        digits=dp.get_precision("Product Price"),
        store=True)
    categ_id = fields.Many2one(
        comodel_name="product.category", related="product_id.categ_id",
        string="Category", store=True)
    service_type = fields.Many2one(
        comodel_name="service.type", string="Service Type")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super()._onchange_product_id()
        if self.product_id:
            self.service_type = self.product_id.categ_id.service_type

    @api.depends("product_id", "product_id.standard_price", "supplier_price")
    def _compute_standard_price(self):
        for line in self.filtered("product_id"):
            if line.supplier_price:
                line.standard_price = line.supplier_price
            else:
                super(MrpProductionProductLine, line)._compute_standard_price()

    # @api.depends("sale_line_id")
    # def _compute_bom_products(self):
    #     for line in self:
    #         if line.sale_line_id:
    #             product = line.sale_line_id.product_id

    @api.onchange("supplier_subtotal")
    def _onchange_percents(self):
        for mrp in self:
            mrp.profit = (
                mrp.supplier_subtotal *
                (mrp.production_id.profit_percent / 100))
            mrp.commercial = (
                (mrp.supplier_subtotal + mrp.profit) *
                (mrp.production_id.commercial_percent / 100))
            mrp.external_commercial = (
                (mrp.supplier_subtotal + mrp.profit) *
                (mrp.production_id.external_commercial_percent / 100))

    @api.depends("supplier_subtotal", "profit", "commercial",
                 "external_commercial")
    def _compute_profit(self):
        for mrp in self:
            mrp.price = (
                mrp.supplier_subtotal + mrp.profit + mrp.commercial +
                mrp.external_commercial)
