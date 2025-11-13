# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    is_incubator = fields.Boolean(
        string="Incubator", related="location_id.is_incubator", store=True
    )
    is_integration = fields.Boolean(
        string="Integration", related="location_id.is_integration", store=True
    )
    is_reproductor = fields.Boolean(
        string="Reproductor", related="location_id.is_reproductor", store=True
    )
    is_feed_flour = fields.Boolean(
        string="Feed/Flour", related="location_id.is_feed_flour", store=True
    )
    is_medicine = fields.Boolean(
        string="Medicine", related="location_id.is_medicine", store=True
    )

    def _get_inventory_cost(self):
        if self.lot_id and self.lot_id.average_price:
            return self.lot_id.average_price
        else:
            return self.product_id.standard_price or 0.0

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        vals = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out=out
        )
        cost = self._get_inventory_cost()
        move_lines = vals.get("move_line_ids", [])
        move_qty_done = 0.0
        for _, _, move_line_vals in move_lines:
            qty_done = abs(move_line_vals.get("qty_done", 0.0))
            move_line_vals.update(
                {
                    "standard_price": cost,
                    "amount": cost * qty_done,
                }
            )
            move_qty_done += qty_done
        vals.update(
            {
                "standard_price": cost,
                "amount": cost * move_qty_done,
            }
        )
        return vals
