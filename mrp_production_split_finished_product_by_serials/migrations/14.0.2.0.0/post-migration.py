# Copyright 2024 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

# pylint: disable=W8150
from odoo.addons.mrp_production_split_finished_product_by_serials.hooks import (
    post_init_hook,
)

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Trigger again the post_init_hook")
    env = api.Environment(cr, SUPERUSER_ID, {})
    post_init_hook(cr, env.registry)
