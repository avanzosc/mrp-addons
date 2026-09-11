# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    laser_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Laser Cutting Bill of Materials",
        help="Bill of Materials proposed by default on new laser cutting "
        "orders. Its product is the generic item manufactured by the "
        "manufacturing orders they generate.",
    )
    laser_offcut_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Laser Cutting Offcut Product",
        help="Generic, consumable product proposed by default as the "
        "consumed material on laser cutting orders flagged to use offcut "
        "(remnant) material.",
    )
