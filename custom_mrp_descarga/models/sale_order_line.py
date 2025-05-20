# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_average_price = fields.Float(
        digits="MRP Price Decimal Precision",
    )
    lot_cost = fields.Float()

    def _compute_average_price(self):
        query = """
            WITH lot_prices AS (
                SELECT
                    lot_id,
                    SUM(amount) AS total_amount,
                    SUM(qty_done) AS total_qty
                FROM
                    stock_move_line
                WHERE
                    state = 'done'
                    AND location_dest_id IN (SELECT id
                        FROM stock_location WHERE usage = 'internal')
                    AND location_id IN (SELECT id
                        FROM stock_location WHERE usage != 'internal')
                GROUP BY
                    lot_id
            )
            UPDATE sale_order_line sol
            SET
                lot_average_price = lp.total_amount / lp.total_qty,
                lot_cost = (lp.total_amount / lp.total_qty) * sol.product_uom_qty
            FROM lot_prices lp
            WHERE sol.lot_id = lp.lot_id
            AND lp.total_qty != 0;
            UPDATE sale_order_line
            SET lot_average_price = 0
            WHERE lot_average_price IS NULL;
            UPDATE sale_order_line
            SET lot_cost = 0
            WHERE lot_cost IS NULL;
        """
        self.env.cr.execute(query)
