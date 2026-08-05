# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    laser_generic_product_id = fields.Many2one(
        related="company_id.laser_generic_product_id", readonly=False
    )
    laser_bom_id = fields.Many2one(related="company_id.laser_bom_id", readonly=False)
    laser_scrap_product_id = fields.Many2one(
        related="company_id.laser_scrap_product_id", readonly=False
    )
