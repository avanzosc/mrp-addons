# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_qty_available = fields.Float(
        string="Stock Available",
        compute="_compute_product_qty_available",
        digits="Product Unit of Measure",
    )

    def _compute_product_qty_available(self):
        for move in self:
            move.product_qty_available = move.with_context(
                location=move.location_id.id
            ).qty_available
