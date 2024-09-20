# Copyright 2024 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class QcInspectionTipe(models.Model):
    _name = "qc.inspection.type"
    _description = "Inspections types"
    _order = "name"

    name = fields.Char(string="Description")
