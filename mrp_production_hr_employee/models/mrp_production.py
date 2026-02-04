from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    employee_ids = fields.Many2many(
        "hr.employee",
        "mrp_production_hr_employee_rel",
        "production_id",
        "employee_id",
        string="Employees",
    )
