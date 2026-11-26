# Copyright 2026 AvanzOSC - Lucía Echeverría
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    multiple_serial_production = fields.Boolean(
        default=True,
        help="If checked, manufacturing orders of serial-tracked products "
        "produce all their units at once, with one serial number per finished "
        "move line. If unchecked, they work as standard: one serial number at "
        "a time, set in the Lot/Serial Number field of the manufacturing order.",
    )
