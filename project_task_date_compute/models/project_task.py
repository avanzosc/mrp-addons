# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = "project.task"

    start_date = fields.Date(
        string="Start Date", 
        compute="_compute_start_date", 
        store=True
    )
    end_date = fields.Date(
        string="End Date", 
        compute="_compute_end_date", 
        store=True
    )

    @api.depends("timesheet_ids.date")
    def _compute_start_date(self):
        _logger.info("Calculating start dates for tasks...")
        for task in self:
            task.start_date = min(task.timesheet_ids.mapped('date'), default=False)
            _logger.info(f"Task {task.name} - Start Date: {task.start_date}")

    @api.depends("timesheet_ids.date")
    def _compute_end_date(self):
        _logger.info("Calculating end dates for tasks...")
        for task in self:
            if task.stage_id.fold:
                task.end_date = max(task.timesheet_ids.mapped('date'), default=False)
                _logger.info(f"Task {task.name} - End Date: {task.end_date}")
            else:
                task.end_date = False
                _logger.info(f"Task {task.name} - End Date: None (not folded)")

