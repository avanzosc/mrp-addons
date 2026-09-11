# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    laser_cut_order_id = fields.Many2one(
        comodel_name="mrp.laser.cut.order",
        string="Laser Cutting Order",
        copy=True,
        index=True,
        help="Laser cutting order that generated this manufacturing order.",
    )
