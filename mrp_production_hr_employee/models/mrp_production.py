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

    def action_open_wizard(self):
        self.ensure_one()
        return {
            "name": "Work Order",
            "type": "ir.actions.act_window",
            "res_model": "mrp.production",
            "res_id": self.id,
            "view_mode": "form",
            "views": [
                (
                    self.env.ref("mrp.mrp_production_form_view").id,
                    "form",
                )
            ],
            "target": "current",
        }
