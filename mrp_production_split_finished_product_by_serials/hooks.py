# Copyright 2024 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

try:
    from openupgradelib import openupgrade
except Exception:
    from odoo.tools import sql as openupgrade


_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Add production lot name as field
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE mrp_production m
        SET serial_lot_name = (
            SELECT name FROM stock_lot l WHERE l.id = m.lot_producing_id LIMIT 1)
        WHERE lot_producing_id IS NOT NULL;
        """,
    )
