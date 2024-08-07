from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    sale_price_subtotal = fields.Float(
        "Subtotal",
        compute="_compute_sale_price_subtotal",
        store=True,
    )

    @api.depends("product_id.lst_price", "product_qty")
    def _compute_sale_price_subtotal(self):
        for line in self:
            if line.product_id and line.product_qty:
                line.sale_price_subtotal = line.product_id.lst_price * line.product_qty
            else:
                line.sale_price_subtotal = 0.0
