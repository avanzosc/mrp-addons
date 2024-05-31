# Copyright 2024 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade

from odoo.addons.mrp_usability.hooks import related_fields, related_models, relations, store_related_fields


logger = logging.getLogger(__name__)

@openupgrade.migrate()
def migrate(env, version):
    store_related_fields(env.cr, related_models, related_fields, relations)
