# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    laser_generic_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Laser Cutting Generic Product",
        help="Generic, consumable product used as the product to "
        "manufacture on every manufacturing order generated from a laser "
        "cutting order.",
    )
    laser_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Laser Cutting Bill of Materials",
        help="Bill of Materials of the laser cutting generic product, "
        "used by default on new laser cutting orders.",
    )
    laser_scrap_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Laser Cutting Scrap Product",
        help="Generic, consumable product used by default as the "
        "consumed material on laser cutting orders flagged as using "
        "scrap/offcut material.",
    )
