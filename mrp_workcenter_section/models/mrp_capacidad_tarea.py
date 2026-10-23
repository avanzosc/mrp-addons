# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpCapacidadTarea(models.Model):
    _name = "mrp.capacidad.tarea"
    _description = "Tarea de capacidad de producción"

    name = fields.Char(string="Nombre")
    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        string="Centro de producción original",
    )
