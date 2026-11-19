from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.template"

    subcon_operations = fields.Boolean(
        string="suncontracting in operations",
    )

    subcontracting_charge_ids = fields.One2many(
        "product.subcontracting.charge",
        "parent_product_id",
        string="Additional charges",
    )
