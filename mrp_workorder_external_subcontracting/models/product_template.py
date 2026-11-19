from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    subcon_operations = fields.Boolean(string="Subcontracting in Operations")
    subcontracting_charge_ids = fields.One2many(
        comodel_name="product.subcontracting.charge",
        inverse_name="parent_product_id",
        string="Additional Charges",
    )
