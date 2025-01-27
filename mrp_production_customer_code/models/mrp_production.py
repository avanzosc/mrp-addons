from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    product_customer_code = fields.Char(
        "Customer Code", compute="_compute_product_customer_code", store=True
    )

    @api.depends("product_id", "partner_id")
    def _compute_product_customer_code(self):
        for production in self:
            if not production.product_id or not production.partner_id:
                production.product_customer_code = False
                continue

            customer_info = self.env["product.customerinfo"].search(
                [
                    ("partner_id", "=", production.partner_id.id),
                    "|",
                    ("product_id", "=", production.product_id.id),
                    ("product_tmpl_id", "=", production.product_id.product_tmpl_id.id),
                ],
                order="product_id DESC",
                limit=1,
            )

            production.product_customer_code = (
                customer_info.product_code if customer_info else False
            )
