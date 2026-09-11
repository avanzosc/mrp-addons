# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    is_laser = fields.Boolean(
        string="Laser Work Center",
        help="Mark work centers that perform laser cutting. The component "
        "consumed by an operation on such a work center is treated as the "
        "raw material of the product it produces.",
    )
