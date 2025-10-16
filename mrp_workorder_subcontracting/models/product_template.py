from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.template"

    subcon_operations = fields.Boolean(
        string="suncontracting in operations",
    )
