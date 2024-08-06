# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    last_mrp_id = fields.Many2one(
        string="Last Manufacturing Order",
        comodel_name="mrp.production",
        compute="_compute_last_mrp_info",
    )
    last_mrp_date = fields.Datetime(
        string="Last Manufacturing Order Date", compute="_compute_last_mrp_info"
    )

    def _compute_last_mrp_info(self):
        for product in self:
            production = self.env["mrp.production"].search(
                [("product_id", "=", product.id), ("state", "=", "done")],
                limit=1,
                order="date_finished desc",
            )
            product._get_last_mrp_info(production)

    def _get_last_mrp_info(self, production):
        self.last_mrp_id = production.id
        self.last_mrp_date = production.date_finished
