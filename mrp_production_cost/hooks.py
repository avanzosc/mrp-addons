import logging

from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def install_mrp_workorder_cost(cr):
    _logger.info("mrp_production_cost: Setting cost for mrp_workorder")
    env = api.Environment(cr, SUPERUSER_ID, {})
    cond = [("costs_hour", ">", 0)]
    workcenters = env["mrp.workcenter"].search(cond)
    for workcenter in workcenters:
        cr.execute(
            """
            UPDATE mrp_workorder
            SET machine_hour_cost = %s
            WHERE workcenter_id IS NOT NULL AND workcenter_id = %s;
            """,
            (
                workcenter.costs_hour,
                workcenter.id,
            ),
        )
    cr.execute(
        """
        UPDATE mrp_workorder
        SET workorder_cost_estimated = machine_hour_cost * duration_expected
        WHERE machine_hour_cost > 0
          AND duration_expected > 0;
        """
    )
    cr.execute(
        """
        UPDATE mrp_workorder
        SET workorder_cost_real = (machine_hour_cost / 60) * duration
        WHERE machine_hour_cost > 0
          AND duration > 0;
        """
    )


def install_stock_move_cost(cr):
    _logger.info("mrp_production_cost: Calculating cost for stock moves")
    cr.execute(
        """
        UPDATE stock_move
        SET material_cost_to_consume = price_unit_cost * product_uom_qty
        WHERE price_unit_cost > 0
          AND product_uom_qty > 0;
        """
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    cond = [("price_unit_cost", ">", 0)]
    moves = env["stock.move"].search(cond)
    for move in moves.filtered(lambda x: x.quantity_done > 0):
        cr.execute(
            """
            UPDATE stock_move
            SET material_cost_consumed = %s * %s
            WHERE ID = %s;
            """,
            (move.price_unit, move.quantity_done, move.id),
        )


def install_mrp_production_cost(cr):
    _logger.info("mrp_production_cost: Calculating cost for mrp production")
    cr.execute(
        """
        UPDATE mrp_production mp
        SET cost_material_to_consume = COALESCE(sub.total_cost, 0)
        FROM (
            SELECT
                mp2.id AS production_id,
                SUM(sm.material_cost_to_consume) AS total_cost
            FROM mrp_production mp2
            LEFT JOIN stock_move sm
                ON sm.raw_material_production_id = mp2.id
            GROUP BY mp2.id
        ) sub
        WHERE mp.id = sub.production_id;
        """
    )
    cr.execute(
        """
        UPDATE mrp_production mp
        SET cost_material_consumed = COALESCE(sub.total_cost, 0)
        FROM (
            SELECT
                mp2.id AS production_id,
                SUM(sm.material_cost_consumed) AS total_cost
            FROM mrp_production mp2
            LEFT JOIN stock_move sm
                ON sm.raw_material_production_id = mp2.id
            GROUP BY mp2.id
        ) sub
        WHERE mp.id = sub.production_id;
        """
    )
    cr.execute(
        """
        UPDATE mrp_production mp
        SET cost_workorder_estimated = COALESCE(sub.total_cost, 0)
        FROM (
            SELECT
                mp2.id AS production_id,
                SUM(mw.workorder_cost_estimated) AS total_cost
            FROM mrp_production mp2
            LEFT JOIN mrp_workorder mw
                ON mw.production_id = mp2.id
            GROUP BY mp2.id
        ) sub
        WHERE mp.id = sub.production_id;
        """
    )
    cr.execute(
        """
        UPDATE mrp_production mp
        SET cost_workorder_real = COALESCE(sub.total_cost, 0)
        FROM (
            SELECT
                mp2.id AS production_id,
                SUM(mw.workorder_cost_real) AS total_cost
            FROM mrp_production mp2
            LEFT JOIN mrp_workorder mw
                ON mw.production_id = mp2.id
            GROUP BY mp2.id
        ) sub
        WHERE mp.id = sub.production_id;
        """
    )
    cr.execute(
        """
        UPDATE mrp_production
        SET cost_manufacturing_estimated =
            COALESCE(cost_material_to_consume, 0)
            + COALESCE(cost_workorder_estimated, 0);
        """
    )
    cr.execute(
        """
        UPDATE mrp_production
        SET cost_manufacturing_real =
            COALESCE(cost_material_consumed, 0)
            + COALESCE(cost_workorder_real, 0);
        """
    )
    cr.execute(
        """
        UPDATE mrp_production
        SET price_unit_cost = CASE
            WHEN qty_producing != 0 THEN
                COALESCE(cost_manufacturing_real, 0) / qty_producing
            ELSE
                0
        END;
        """
    )


def _pre_init_mrp_production_cost(cr):
    _logger.info("mrp_production_cost: Starting pre-init hook")
    if not column_exists(cr, "mrp_workorder", "machine_hour_cost"):
        create_column(cr, "mrp_workorder", "machine_hour_cost", "numeric")
    if not column_exists(cr, "mrp_workorder", "workorder_cost_estimated"):
        create_column(cr, "mrp_workorder", "workorder_cost_estimated", "numeric")
    if not column_exists(cr, "mrp_workorder", "workorder_cost_real"):
        create_column(cr, "mrp_workorder", "workorder_cost_real", "numeric")
    if not column_exists(cr, "stock_move", "material_cost_to_consume"):
        create_column(cr, "stock_move", "material_cost_to_consume", "numeric")
    if not column_exists(cr, "stock_move", "material_cost_consumed"):
        create_column(cr, "stock_move", "material_cost_consumed", "numeric")
    if not column_exists(cr, "mrp_production", "cost_material_to_consume"):
        create_column(cr, "mrp_production", "cost_material_to_consume", "numeric")
    if not column_exists(cr, "mrp_production", "cost_material_consumed"):
        create_column(cr, "mrp_production", "cost_material_consumed", "numeric")
    if not column_exists(cr, "mrp_production", "cost_workorder_estimated"):
        create_column(cr, "mrp_production", "cost_workorder_estimated", "numeric")
    if not column_exists(cr, "mrp_production", "cost_workorder_real"):
        create_column(cr, "mrp_production", "cost_workorder_real", "numeric")
    if not column_exists(cr, "mrp_production", "cost_manufacturing_estimated"):
        create_column(cr, "mrp_production", "cost_manufacturing_estimated", "numeric")
    if not column_exists(cr, "mrp_production", "cost_manufacturing_real"):
        create_column(cr, "mrp_production", "cost_manufacturing_real", "numeric")
    if not column_exists(cr, "mrp_production", "price_unit_cost"):
        create_column(cr, "mrp_production", "price_unit_cost", "numeric")
    _logger.info("mrp_production_cost: Pre-init hook completed")


def _post_init_mrp_production_cost(cr, registry):
    _logger.info("mrp_production_cost: Starting post-init hook")
    install_mrp_workorder_cost(cr)
    install_stock_move_cost(cr)
    install_mrp_production_cost(cr)
    _logger.info("mrp_production_cost: Post-init hook completed")
