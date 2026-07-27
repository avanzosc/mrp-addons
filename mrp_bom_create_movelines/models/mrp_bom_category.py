# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBomCategory(models.Model):

    _inherit = "mrp.bom.category"

    bring_components_on_confirm = fields.Boolean(
        string="Bring Components on Confirm",
        default=False,
        help="When confirming a production order with this category, "
        "automatically create input lines for all storable BOM components "
        "without requiring lot reservation.",
    )
