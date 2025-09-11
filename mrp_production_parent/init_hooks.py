# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

try:
    from openupgradelib import openupgrade
except Exception:
    from odoo.tools import sql as openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info(
        "Pre-creating column mrp_production_parent_id for table mrp_production"
    )
    if not openupgrade.column_exists(cr, "mrp_production", "mrp_production_parent_id"):
        cr.execute(
            """
            ALTER TABLE mrp_production
            ADD COLUMN mrp_production_parent_id float;
            COMMENT ON COLUMN mrp_production.mrp_production_parent_id
            IS 'Production Parent';
            """
        )


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        force_compute_sale_order(env)


def force_compute_sale_order(env):
    cond = [("origin", "!=", False)]
    productions = env["mrp.production"].search(cond, order="id asc")
    _logger.info("Force-compute Production Parent on %s productions" % len(productions))
    for production in productions:
        cond = [("name", "=", production.origin)]
        production_parent = env["mrp.production"].search(cond, limit=1)
        if production_parent:
            vals = {"mrp_production_parent_id": production_parent.id}
            if production_parent.sale_id:
                vals["sale_id"] = production_parent.sale_id
                if production_parent.sale_id.commitment_date:
                    vals["commitment_date"] = production_parent.sale_id.commitment_date
            production.write(vals)
