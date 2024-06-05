# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    layer = fields.Char()
    designator = fields.Char()
