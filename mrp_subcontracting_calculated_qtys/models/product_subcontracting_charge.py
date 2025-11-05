from odoo import api, fields, models


class ProductSubcontractingCharge(models.Model):
    _inherit = "product.subcontracting.charge"
    quantity_calculation = fields.Selection(
        selection_add=[("feeders", "Feeders"), ("caras_a_montar", "Caras a montar")],
    )

    @api.model
    def compute_charge_qty(self, production):
        self.ensure_one()
        qty = 0.0

        if self.quantity_calculation == "feeders":
            qty = sum(
                line.product_qty
                for line in production.bom_id.bom_line_ids
                if line.layer in ("TOP", "BOT")
            )

        elif self.quantity_calculation == "caras_a_montar":
            qty = (
                2
                if any(line.layer == "BOT" for line in production.bom_id.bom_line_ids)
                else 1
            )

        return qty
