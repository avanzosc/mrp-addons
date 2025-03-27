# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_immediately_usable_qty = fields.Float(
        string="Available",
        related="product_id.immediately_usable_qty",
        digits="Product Unit of Measure",
    )
