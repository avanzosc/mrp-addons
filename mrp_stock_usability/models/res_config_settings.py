# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_mrp_stock_usability = fields.Boolean(
        string="Stock Usability in Manufacturing",
        implied_group="mrp_stock_usability.group_mrp_stock_usability",
    )
