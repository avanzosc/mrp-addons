from odoo import api, fields, models


class ProductSubcontractingCharge(models.Model):
    _inherit = "product.subcontracting.charge"

    quantity_calculation = fields.Selection(
        selection_add=[
            ("feeders", "Feeders"),
            ("caras_a_montar", "Caras a montar"),
            ("tarifa_fija", "Tarifa_fija"),
        ],
    )

    @api.model
    def compute_qty(self, production, type_charge=None):
        qty_production = production.product_qty
        qty = qty_production

        bom_components = sum(
            line.product_qty
            for line in production.bom_id.bom_line_ids
            if line.layer in ("TOP", "BOT")
        )

        if type_charge == "standard":
            qty = qty_production * bom_components
        elif type_charge == "feeders":
            bom_top_lines = len(
                [
                    line
                    for line in production.bom_id.bom_line_ids
                    if line.layer in ("TOP", "BOT")
                ]
            )
            qty = bom_top_lines
        elif type_charge == "caras_a_montar":
            qty = (
                2
                if any(line.layer == "BOT" for line in production.bom_id.bom_line_ids)
                else 1
            )
        elif type_charge == "tarifa_fija":
            qty = 1

        return qty
