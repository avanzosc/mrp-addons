# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    laser_order_id = fields.Many2one(
        comodel_name="order.olaser",
        string="Laser Cutting Order",
        copy=True,
        index=True,
        help="Laser cutting order that generated this manufacturing order.",
    )
