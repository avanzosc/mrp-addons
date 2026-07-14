# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    production_department = fields.Boolean(string="Production Depart.", default=False)
