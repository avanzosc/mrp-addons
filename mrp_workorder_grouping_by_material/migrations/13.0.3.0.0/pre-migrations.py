# Copyright 2023 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            mrp_workorder_nest_line
        SET
            state = 'done'
        WHERE
            state NOT IN ('done', 'cancel')
        AND
            workorder_id IN (SELECT id FROM mrp_workorder WHERE state = 'done')
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            mrp_workorder_nest_line
        SET
            state = 'cancel'
        WHERE
            state NOT IN ('done', 'cancel')
        AND
            workorder_id IN (SELECT id FROM mrp_workorder WHERE state = 'cancel')
        """,
    )
