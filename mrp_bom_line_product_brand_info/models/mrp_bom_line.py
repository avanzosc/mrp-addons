# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    seller_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        domain="['|', ('product_id', '=', product_id), '&', "
        "('product_tmpl_id', '=', product_tmpl_id), "
        "('product_id', '=', False)]",
    )
    product_name = fields.Char(
        related="seller_id.product_name",
        store=True,
    )
    product_code = fields.Char(
        related="seller_id.product_code",
        store=True,
    )
    manufacturer_codes = fields.Char(related="seller_id.brand_code", store=True)
    markings = fields.Many2one(
        comodel_name="product.brand",
        related="seller_id.product_brand_id",
        store=True,
    )
