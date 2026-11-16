# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    laser_bom_id = fields.Many2one(related="company_id.laser_bom_id", readonly=False)
    laser_offcut_product_id = fields.Many2one(
        related="company_id.laser_offcut_product_id", readonly=False
    )
