# Copyright 2026 Inael
# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    laser_cut_order_id = fields.Many2one(
        comodel_name="mrp.laser.cut.order",
        string="Laser Cutting Order",
        index=True,
        copy=False,
        help="Laser cutting order this stock move belongs to. Set on the "
        "consumption and by-product moves of the generated manufacturing "
        "order, so the order can report what it really consumed and produced "
        "even when no manufacturing order is involved.",
    )
    laser_cut_order_line_id = fields.Many2one(
        comodel_name="mrp.laser.cut.order.line",
        string="Laser Cutting Order Line",
        index=True,
        copy=False,
        help="Distribution line of the laser cutting order this by-product "
        "move corresponds to.",
    )
