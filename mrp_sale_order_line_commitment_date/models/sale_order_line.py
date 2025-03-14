from odoo import models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, vals):
        res = super().write(vals)
        if "commitment_date" in vals:

            order_origin = self.order_id.name
            productions = self.env["mrp.production"].search(
                [("origin", "like", f"{order_origin}")]
            )
            productions._compute_sale_order_line_commitment_date()
        
        return res
