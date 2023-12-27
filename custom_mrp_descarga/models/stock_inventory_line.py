# © 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    cost = fields.Float(
        digits="Standard Cost Decimal Precision",
    )

    @api.onchange("product_id", "prod_lot_id")
    def onchange_cost(self):
        super(StockInventoryLine, self).onchange_cost()
        if self.prod_lot_id and self.prod_lot_id.average_price:
            self.cost = self.prod_lot_id.average_price
