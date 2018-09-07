# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_editable_scheduled_products = fields.Boolean(
        string="Editable Scheduled Products",
        implied_group="mrp_scheduled_products."
                      "group_editable_scheduled_products")
