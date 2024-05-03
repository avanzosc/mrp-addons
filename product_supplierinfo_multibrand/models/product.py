# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = "supplier.brand"

    supplier_brand_name = fields.Char(string="Name")
    supplier_brand_code = fields.Char(string="Code")
    supplier_id = fields.Many2one(comodel_name="product.supplierinfo", string="Partner")
    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")
    product_tmpl_id = fields.Many2one(comodel_name="product.template", string="product")
    product_internal_reference = fields.Char(
        string="Product internal reference",
        store=True,
        related="product_tmpl_id.prefix_code",
    )


class ProductProduct(models.Model):
    _inherit = "product.template"

    supplier_brand = fields.One2many(
        comodel_name="supplier.brand", inverse_name="product_tmpl_id"
    )
    possible_suppliers = fields.Many2many(
        comodel_name="product.supplierinfo", compute="_get_possible_suppliers"
    )
    possible_brands = fields.Many2many(
        comodel_name="product.brand", compute="_get_possible_brands"
    )

    @api.depends("brand_ids")
    def _get_possible_brands(self):
        for product in self:
            product.possible_brands = [(6, 0, product.brand_ids._ids)]

    @api.depends("seller_ids")
    def _get_possible_suppliers(self):
        for product in self:
            supplierinfo_ids = product.seller_ids._ids
            product.possible_suppliers = [(6, 0, supplierinfo_ids)]
