# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_qty_available = fields.Float(
        string="Quantity On Hand",
        related="product_id.qty_available",
        digits="Product Unit of Measure",
    )
    product_qty_available_not_res = fields.Float(
        string="Qty Available Not Reserved",
        related="product_id.qty_available_not_res",
        digits="Product Unit of Measure",
    )
