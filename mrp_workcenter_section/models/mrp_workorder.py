# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    tarea_id = fields.Many2one(
        comodel_name="mrp.capacidad.tarea",
        string="Tarea",
    )

    section_id = fields.Many2one(
        comodel_name="mrp.workcenter.section",
        string="Sección",
        related="workcenter_id.section_id",
        store=True,
        index=True,
    )
    workcenter_id = fields.Many2one(
        group_expand=None,
    )
