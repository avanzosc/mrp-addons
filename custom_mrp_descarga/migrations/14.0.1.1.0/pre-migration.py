# Copyright 2025 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.column_exists(cr, "sale_order_line", "lot_average_price"):
        cr.execute(
            """
            ALTER TABLE sale_order_line
            ADD COLUMN lot_average_price float;
            """
        )
        cr.execute(
            """
        UPDATE sale_order_line
        SET     lot_average_price = (SELECT stock_production_lot.average_price
                                FROM    stock_production_lot
                                WHERE stock_production_lot.id = sale_order_line.lot_id)
            """
        )
    if not openupgrade.column_exists(cr, "sale_order_line", "lot_cost"):
        cr.execute(
            """
            ALTER TABLE sale_order_line
            ADD COLUMN lot_cost float;
            """
        )
        cr.execute(
            """
        UPDATE sale_order_line
        SET     lot_cost = (SELECT stock_production_lot.average_price * product_uom_qty
                                FROM    stock_production_lot
                                WHERE stock_production_lot.id = sale_order_line.lot_id)
            """
        )
