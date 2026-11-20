# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    section_id = fields.Many2one(
        comodel_name="mrp.workcenter.section",
        string="Sección",
        index=True,
    )
