# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute(
        """
        UPDATE mrp_production m
        SET sale_order_id = (
            SELECT order_id
            FROM sale_order_line s
            WHERE s.id = m.sale_line_id)
        WHERE sale_line_id IS NOT NULL
        AND sale_order_id IS NULL;
        """)
