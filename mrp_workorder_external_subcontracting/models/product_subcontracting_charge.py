from odoo import api, fields, models


class ProductSubcontractingCharge(models.Model):
    _name = "product.subcontracting.charge"
    _description = "Subcontracting Charge"

    parent_product_id = fields.Many2one(
        comodel_name="product.template",
        string="Service Product",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        comodel_name="product.template",
        string="Additional Charge",
        required=True,
    )
    quantity_calculation = fields.Selection(
        selection=[("standard", "Standard")],
        string="Calculation Type",
        default="standard",
        required=True,
    )

    @api.model
    def compute_qty(self, production, type_charge=None):
        return production.product_qty
