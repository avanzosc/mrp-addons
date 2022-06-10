# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    is_deconstruction = fields.Boolean(
        string="Is Deconstruction?", default=False)
