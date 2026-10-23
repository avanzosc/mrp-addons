# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkcenterSection(models.Model):
    _name = "mrp.workcenter.section"
    _description = "Workcenter Section"

    name = fields.Char(string="Nombre", required=True)
