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

    def action_open_production_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "mrp.production",
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
        }
