from odoo import api, fields, models


class ProductSubcontractingCharge(models.Model):
    _name = "product.subcontracting.charge"
    _description = "Subcontracting Charge"

    parent_product_id = fields.Many2one(
        "product.template",
        string="Product service",
        required=True,
    )

    product_id = fields.Many2one(
        "product.template",
        string="Additional charge",
        required=True,
    )

    quantity_calculation = fields.Selection(
        [("standard", "Standard")],
        string="Calculation type",
        default="standard",
    )

    @api.model
    def compute_charge_qty(self, production):
        self.ensure_one()
        qty = 0.0

        if self.quantity_calculation == "standard":
            qty = production.qty_producing
        return qty
