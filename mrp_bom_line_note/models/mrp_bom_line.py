# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom.line"

    note = fields.Text()
