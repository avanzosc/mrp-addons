# Copyright 2024 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.column_exists(cr, "stock_move_line", "operation_id"):
        cr.execute(
            """
            ALTER TABLE stock_move_line
            ADD COLUMN operation_id integer;
            """
        )
        cr.execute(
            """
        UPDATE stock_move_line
        SET     operation_id = (SELECT mrp_bom_byproduct.operation_id
                                FROM    mrp_bom_byproduct,
                                        stock_move
                                WHERE stock_move.id = stock_move_line.move_id
                                AND move_id IS NOT NULL
                                AND mrp_bom_byproduct.id = stock_move.byproduct_id
                                AND byproduct_id IS NOT NULL)
            """
        )
