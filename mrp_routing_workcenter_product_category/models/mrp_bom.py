from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    categ_id = fields.Many2one(
        "product.category",
        related="product_tmpl_id.categ_id",
        store=True,
        string="product category",
    )
