# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.mrp_production_custom_variants_inherited_attributes.hooks import \
    post_init_hook


def migrate(cr, version):
    post_init_hook(cr, False)
