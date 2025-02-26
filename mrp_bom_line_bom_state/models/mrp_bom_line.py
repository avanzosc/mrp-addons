# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    bom_state = fields.Selection(
        string="BoM Status", related="bom_id.state", store=True
    )
