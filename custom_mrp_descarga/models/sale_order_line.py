# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_average_price = fields.Float(
        digits="MRP Price Decimal Precision",
        compute="_compute_average_price",
    )
    lot_cost = fields.Float(compute="_compute_lot_cost")

    @api.depends("lot_id", "lot_id.average_price")
    def _compute_average_price(self):
        for line in self:
            lot_average_price = 0
            if line.lot_id:
                lot_average_price = line.lot_id.average_price
            line.lot_average_price = lot_average_price

    @api.depends("lot_average_price", "product_uom_qty")
    def _compute_lot_cost(self):
        for line in self:
            line.lot_cost = line.lot_average_price * line.product_uom_qty
