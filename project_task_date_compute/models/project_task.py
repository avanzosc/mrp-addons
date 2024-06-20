from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = "project.task"

    start_date = fields.Datetime(
        string="Start Date", 
        compute="_compute_dates", 
        store=True
    )
    end_date = fields.Datetime(
        string="End Date", 
        compute="_compute_dates", 
        store=True
    )
    create_date = fields.Datetime(
        string="Creation Date", 
        readonly=True
    )

    @api.depends("timesheet_ids.date", "stage_id.fold")
    def _compute_dates(self):
        for task in self:
            if task.timesheet_ids:
                dates = task.timesheet_ids.mapped("date")
                task.start_date = min(dates)
                if task.stage_id.fold:
                    task.end_date = max(dates)
                else:
                    task.end_date = False
            else:
                task.start_date = task.end_date = False
