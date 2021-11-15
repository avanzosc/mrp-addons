# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        CREATE TABLE IF NOT EXISTS
            mrp_workorder_mrp_workorder_nest_rel (
                mrp_workorder_id int,
                mrp_workorder_nest_id int
            );""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE 
            mrp_workorder
        ADD COLUMN
            nested_count int,
        ADD COLUMN
            qty_nested float8;""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM
            mrp_workorder_nest_line
        WHERE
            workorder_id IS NULL
        OR
            nest_id IS NULL;
        """
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO
            mrp_workorder_mrp_workorder_nest_rel
                (mrp_workorder_id, mrp_workorder_nest_id)
        SELECT 
            workorder_id,
            nest_id
        FROM
            mrp_workorder_nest_line
        ON CONFLICT DO NOTHING;
        """
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            mrp_workorder wo
        SET
            nested_count = (
                SELECT
                    COUNT(DISTINCT(mrp_workorder_nest_id))
                FROM 
                    mrp_workorder_mrp_workorder_nest_rel nest
                WHERE
                    nest.mrp_workorder_id = wo.id); 
        """
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            mrp_workorder wo
        SET
            qty_nested = (
                SELECT
                    SUM(qty_producing)
                FROM
                    mrp_workorder_nest_line line
                WHERE
                    line.workorder_id = wo.id);
        """
    )
