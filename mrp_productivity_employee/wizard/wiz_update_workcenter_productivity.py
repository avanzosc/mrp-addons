# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WizUpdateWorkcenterProductivity(models.TransientModel):
    _name = "wiz.update.workcenter.productivity"
    _description = "Wizard for update workcenter productivity"

    workorder_id = fields.Many2one(string="Work Order", comodel_name="mrp.workorder")
    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    action_type = fields.Selection(
        selection=[
            ("start", "Start"),
            ("finish", "Finish"),
            ("pause", "Pause"),
        ],
    )
    allowed_employee_ids = fields.Many2many(
        comodel_name="hr.employee", string="Allowed employees"
    )
    loss_id = fields.Many2one(
        string="Loss Reason", comodel_name="mrp.workcenter.productivity.loss"
    )

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        result["workorder_id"] = self.env.context.get("default_workorder_id")
        result["action_type"] = self.env.context.get("default_action_type")
        workorder = self.env["mrp.workorder"].browse(result.get("workorder_id"))
        imputations = workorder.time_ids.filtered(
            lambda x: x.employee_id and x.date_start and not x.date_end
        )
        imputation_employees = imputations.mapped("employee_id")
        employees = imputations.mapped("employee_id")
        if result.get("action_type") == "start":
            if workorder.workcenter_id.employee_ids:
                employees = workorder.workcenter_id.employee_ids - imputation_employees
            else:
                cond = [
                    ("id", "not in", employees.ids),
                    ("department_id.production_department", "=", True),
                ]
                employees = self.env["hr.employee"].search(cond)
            result["loss_id"] = self.env.ref("mrp.block_reason7").id
        result["allowed_employee_ids"] = [(6, 0, employees.ids)]
        return result

    def button_start(self):
        self.workorder_id.with_context(
            from_wizard_button_start=True,
            employee_id_ctx=self.employee_id.id,
            loss_id_ctx=self.loss_id.id,
        ).button_start()

    def button_finish(self):
        line = self.workorder_id.time_ids.filtered(
            lambda x: x.employee_id
            and x.employee_id == self.employee_id
            and x.date_start
            and not x.date_end
        )
        if not line:
            message = _(
                "The work order %(workorder_name)s, is already stopped or finished "
                "for the employee %(employe_name)s"
            ) % {
                "workorder_name": self.workorder_id.name,
                "employe_name": self.employee_id.name,
            }
            raise ValidationError(message)
        if self.action_type == "pause":
            self.workorder_id.with_context(
                from_wizard_button_pending=True, default_employee_id=self.employee_id
            ).button_pending()
        else:
            another_worker = self.workorder_id.time_ids.filtered(
                lambda x: x.employee_id
                and x.employee_id != self.employee_id
                and x.date_start
                and not x.date_end
            )
            if another_worker:
                line.date_end = fields.Datetime.now()
            else:
                self.workorder_id.with_context(
                    from_wizard_button_finish=True, default_employee_id=self.employee_id
                ).button_finish()
