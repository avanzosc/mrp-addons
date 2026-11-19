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

    def action_open_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "mrp.production",
            "view_mode": "form",
            "view_id": self.env.ref("mrp.mrp_production_form_view").id,
            "res_id": self.id,
            "target": "current",
        }
