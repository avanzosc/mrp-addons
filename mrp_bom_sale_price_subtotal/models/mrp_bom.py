from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    subtotal = fields.Float(
        compute="_compute_subtotal",
        store=True,
    )

    @api.depends(
        "bom_line_ids",
        "bom_line_ids.product_qty",
        "bom_line_ids.sale_price_subtotal",
    )
    def _compute_subtotal(self):
        for bom in self:
            subtotal = sum(
                line.product_qty * line.product_id.lst_price
                for line in bom.bom_line_ids
            )
            bom.subtotal = subtotal
