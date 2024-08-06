# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    last_mrp_price_unit_cost = fields.Float(
        string="Last Manufacturing Order Cost Unit Price",
        digits="Product Price",
        compute="_compute_last_mrp_info",
    )

    def _get_last_mrp_info(self, production):
        result = super()._get_last_mrp_info(production)
        self.last_mrp_price_unit_cost = production.price_unit_cost
        return result
