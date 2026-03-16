from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def create(self, vals):
        # Create the production record
        production = super().create(vals)

        # Set the 'origin' field if the production has a sale order
        if production.origin:
            sale_name = production.sale_id.name if production.sale_id else ""
            production.origin = f"{production.origin} - {sale_name}"

        # Check if the production has a parent in the manufacturing hierarchy
        parent_productions = self.env["mrp.production"].search([
            ("id", "in", production._get_children()),
            ("origin", "!=", False),
            ("sale_id", "!=", False),
        ])

        # Update child productions' origin field
        for parent in parent_productions:
            production.origin = f"{production.origin} - {parent.sale_id.name}"

        return production
