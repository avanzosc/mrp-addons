# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    tarea = fields.Many2one(comodel_name="mrp.capacidad.tarea")
    section_id = fields.Many2one(
        "mrp.workcenter.section",
        string="Sección",
        related="workcenter_id.section_id",
        store=True,
        index=True,
        readonly=True,
    )
