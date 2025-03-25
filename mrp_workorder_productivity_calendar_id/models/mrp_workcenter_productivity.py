from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Work Schedule",
        required=True,
        help="Work schedule of the employee at the time of this record.",
        default=lambda self: self.env.company.resource_calendar_id,
    )

    @api.onchange("user_id")
    def _onchange_user_id(self):
        """When user_id changes, fetch the employee's work schedule and store it."""
        if self.user_id:
            employee = self.env["hr.employee"].search(
                [("user_id", "=", self.user_id.id)], limit=1
            )
            if employee and employee.resource_calendar_id:
                self.calendar_id = employee.resource_calendar_id
        else:
            self.calendar_id = False

    @api.model
    def create(self, vals):
        """Ensure calendar_id is set when creating a record with a user_id."""
        if vals.get("user_id", False) and "calendar_id" not in vals:
            employee = self.env["hr.employee"].search(
                [("user_id", "=", vals["user_id"])], limit=1
            )
            if employee and employee.resource_calendar_id:
                vals["calendar_id"] = employee.resource_calendar_id.id
        return super(MrpWorkcenterProductivity, self).create(vals)
