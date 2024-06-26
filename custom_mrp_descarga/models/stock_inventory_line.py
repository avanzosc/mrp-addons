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
        if self.inventory_id and self.inventory_id.batch_id:
            if self.prod_lot_id:
                entry_line = self.inventory_id.batch_id.move_line_ids.filtered(
                    lambda c: c.lot_id == self.prod_lot_id and (
                        c.location_dest_id == self.location_id
                    ) and c.picking_id
                )
                dev_line = self.inventory_id.batch_id.move_line_ids.filtered(
                    lambda c: c.lot_id == self.prod_lot_id and (
                        c.location_id == self.location_id
                    ) and c.picking_id
                )
                if entry_line:
                    dev_line_amount = sum(dev_line.mapped("amount")) or 0
                    dev_line_qty = sum(dev_line.mapped("qty_done")) or 0
                    self.cost = (
                        sum(entry_line.mapped("amount")) - dev_line_amount
                    ) / (sum(entry_line.mapped("qty_done")) - dev_line_qty)
            elif self.product_id:
                entry_line = self.inventory_id.batch_id.move_line_ids.filtered(
                    lambda c: c.product_id == self.product_id and (
                        c.location_dest_id == self.location_id
                    ) and c.picking_id
                )
                dev_line = self.inventory_id.batch_id.move_line_ids.filtered(
                    lambda c: c.product_id == self.product_id and (
                        c.location_id == self.location_id
                    ) and c.picking_id
                )
                if entry_line:
                    dev_line_amount = sum(dev_line.mapped("amount")) or 0
                    dev_line_qty = sum(dev_line.mapped("qty_done")) or 0
                    self.cost = (
                        sum(entry_line.mapped("amount")) - dev_line_amount
                    ) / (sum(entry_line.mapped("qty_done")) - dev_line_qty)
