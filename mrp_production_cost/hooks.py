import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def install_stock_move__material_cost_to_consume(env):
    _logger.info("Populating material_cost_to_consume in stock_move...")
    env.cr.execute(
        """
        UPDATE stock_move
        SET material_cost_to_consume = price_unit_cost * product_uom_qty
        where price_unit_cost > 0
          and product_uom_qty > 0;
        """
    )
    _logger.info("material_cost_to_consume populated successfully.")


def install_stock_move__material_cost_consumed(env):
    _logger.info("Populating material_cost_consumed in stock_move...")
    env.cr.execute(
        """
        UPDATE stock_move
        SET material_cost_consumed = price_unit_cost * quantity
        where price_unit_cost > 0
          and quantity > 0;
        """
    )
    _logger.info("material_cost_consumed populated successfully.")


def install_mrp_workorder__workorder_cost_estimated(env):
    _logger.info("Populating workorder_cost_estimated in mrp_workorder...")
    env.cr.execute(
        """
        UPDATE mrp_workorder
        SET workorder_cost_estimated = costs_hour * (duration_expected / 60.0)
        WHERE costs_hour IS NOT NULL
          AND duration_expected IS NOT NULL;
        """
    )
    _logger.info("workorder_cost_estimated populated successfully.")


def install_mrp_workorder__workorder_cost_real(env):
    _logger.info("Populating workorder_cost_real in mrp_workorder...")
    env.cr.execute(
        """
        UPDATE mrp_workorder
        SET workorder_cost_real = costs_hour * (duration / 60.0)
        WHERE costs_hour IS NOT NULL
          AND duration IS NOT NULL;
        """
    )
    _logger.info("workorder_cost_real populated successfully.")


def install_mrp_production_cost_fields(env):
    _logger.info("Updating mrp_production records with computed costs...")
    env.cr.execute(
        """
        UPDATE mrp_production mp
        SET
            cost_material_to_consume = sub.material_est,
            cost_material_consumed = sub.material_real,
            cost_workorder_estimated = sub.wo_est,
            cost_workorder_real = sub.wo_real,
            cost_manufacturing_estimated = (
                COALESCE(sub.material_est, 0) + COALESCE(sub.wo_est, 0)),
            cost_manufacturing_real = (
                COALESCE(sub.material_real, 0) + COALESCE(sub.wo_real, 0)),
            price_unit_cost = CASE
                WHEN mp.qty_producing > 0
                THEN (
                    ((COALESCE(sub.material_real, 0) + COALESCE(sub.wo_real, 0)))
                     / mp.qty_producing)
                ELSE 0
            END
        FROM (
            SELECT
                mp.id AS prod_id,
                SUM(sm.price_unit_cost * sm.product_uom_qty)
                    FILTER (WHERE sm.price_unit_cost > 0 AND sm.product_uom_qty > 0)
                    AS material_est,
                SUM(sm.price_unit_cost * sm.quantity)
                    FILTER (WHERE sm.price_unit_cost > 0 AND sm.quantity > 0)
                    AS material_real,
                SUM(wo.costs_hour * wo.duration_expected / 60.0)
                    FILTER (WHERE wo.costs_hour IS NOT NULL
                        AND wo.duration_expected IS NOT NULL)
                    AS wo_est,
                SUM(wo.costs_hour * wo.duration / 60.0)
                    FILTER (WHERE wo.costs_hour IS NOT NULL AND wo.duration IS NOT NULL)
                    AS wo_real
            FROM mrp_production mp
            LEFT JOIN stock_move sm ON sm.raw_material_production_id = mp.id
            LEFT JOIN mrp_workorder wo ON wo.production_id = mp.id
            GROUP BY mp.id
        ) sub
        WHERE mp.id = sub.prod_id;
        """
    )
    _logger.info("mrp_production cost fields updated successfully.")


def _pre_init_mrp_production_cost(env):
    _logger.info("Starting pre-init for mrp_production_cost module...")

    _logger.info("Adding cost columns to stock_move...")
    if not column_exists(env.cr, "stock_move", "material_cost_to_consume"):
        create_column(env.cr, "stock_move", "material_cost_to_consume", "numeric")
    if not column_exists(env.cr, "stock_move", "material_cost_consumed"):
        create_column(env.cr, "stock_move", "material_cost_consumed", "numeric")

    _logger.info("Adding cost columns to mrp_workorder...")
    if not column_exists(env.cr, "mrp_workorder", "workorder_cost_estimated"):
        create_column(env.cr, "mrp_workorder", "workorder_cost_estimated", "numeric")
    if not column_exists(env.cr, "mrp_workorder", "workorder_cost_real"):
        create_column(env.cr, "mrp_workorder", "workorder_cost_real", "numeric")

    _logger.info("Adding cost fields to mrp_production...")
    if not column_exists(env.cr, "mrp_production", "cost_material_to_consume"):
        create_column(env.cr, "mrp_production", "cost_material_to_consume", "numeric")
    if not column_exists(env.cr, "mrp_production", "cost_material_consumed"):
        create_column(env.cr, "mrp_production", "cost_material_consumed", "numeric")
    if not column_exists(env.cr, "mrp_production", "cost_workorder_estimated"):
        create_column(env.cr, "mrp_production", "cost_workorder_estimated", "numeric")
    if not column_exists(env.cr, "mrp_production", "cost_workorder_real"):
        create_column(env.cr, "mrp_production", "cost_workorder_real", "numeric")
    if not column_exists(env.cr, "mrp_production", "cost_manufacturing_estimated"):
        create_column(
            env.cr,
            "mrp_production",
            "cost_manufacturing_estimated",
            "numeric",
        )
    if not column_exists(env.cr, "mrp_production", "cost_manufacturing_real"):
        create_column(env.cr, "mrp_production", "cost_manufacturing_real", "numeric")
    if not column_exists(env.cr, "mrp_production", "price_unit_cost"):
        create_column(env.cr, "mrp_production", "price_unit_cost", "numeric")

    _logger.info("Pre-init for mrp_production_cost module completed successfully.")


def _post_init_mrp_production_cost(env):
    _logger.info("stock_move_cost: Starting post-init hook")

    install_stock_move__material_cost_to_consume(env)
    install_stock_move__material_cost_consumed(env)
    install_mrp_workorder__workorder_cost_estimated(env)
    install_mrp_workorder__workorder_cost_real(env)
    install_mrp_production_cost_fields(env)

    _logger.info("mrp_production_cost: Post-init hook completed")
