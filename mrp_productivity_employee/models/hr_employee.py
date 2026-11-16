# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    work_center_ids = fields.Many2many(
        string="Work Centers",
        comodel_name="mrp.workcenter",
        relation="rel_mrp_workcenter_employee",
        column1="employee_id",
        column2="workcenter_id",
    )
