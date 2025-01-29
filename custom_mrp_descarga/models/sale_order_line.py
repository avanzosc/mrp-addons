# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_average_price = fields.Float(
        digits="MRP Price Decimal Precision",
        related="lot_id.average_price",
        store=True,
    )
    lot_cost = fields.Float(compute="_compute_lot_cost", store=True)

    @api.depends("lot_average_price", "product_uom_qty")
    def _compute_lot_cost(self):
        for line in self:
            line.lot_cost = line.lot_average_price * line.product_uom_qty
