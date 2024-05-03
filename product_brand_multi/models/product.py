# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models


class ProductBrand(models.Model):
    _name = "product.brand"
    _rec_name = "code"

    product_tmpl_id = fields.Many2one(comodel_name="product.template")
    code = fields.Char(string="Product Code")
    description = fields.Char(string="Description")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    product_internal_reference = fields.Char(
        string="Product internal reference",
        store=True,
        related="product_tmpl_id.prefix_code",
    )
    marking = fields.Char(string="Marking")


class ProductProduct(models.Model):
    _inherit = "product.template"

    brand_ids = fields.One2many(
        comodel_name="product.brand", inverse_name="product_tmpl_id", string="Brands"
    )


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    product_brand_id = fields.Many2one(
        string="Código brand", comodel_name="product.brand"
    )
