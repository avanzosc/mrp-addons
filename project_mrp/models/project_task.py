from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    mrp_production_id = fields.Many2one('mrp.production', string='Manufacturing Order', domain="[('sale_id', '=', sale_line_id.order_id.id)]")
    product_id = fields.Many2one(related='mrp_production_id.product_id', string='Product', store=True)
    verification_by = fields.Selection([
        ('unverified', 'Unverified'),
        ('sent', 'Sent'),
        ('prototype', 'By Prototype'),
        ('antiquity', 'By Antiquity'),
        ('plan', 'By Plan')
    ], string='Verification By')
    preparation = fields.Selection([
        ('closed_box', 'Closed Box'),
        ('open_box', 'Open Box'),
        ('only_bodies', 'Only Bodies'),
        ('only_lids', 'Only Lids'),
        ('only_fronts', 'Only Fronts'),
        ('no_preparation', 'No Preparation')
    ], string='Preparation')
    
    @api.depends('timesheet_ids.date')
    def _compute_start_date(self):
        for task in self:
            task.start_date = min(task.timesheet_ids.mapped('date')) if task.timesheet_ids else False

    @api.depends('timesheet_ids.date')
    def _compute_end_date(self):
        for task in self:
            task.end_date = max(task.timesheet_ids.mapped('date')) if task.timesheet_ids and task.stage_id.is_closing_stage else False

    start_date = fields.Date(compute='_compute_start_date', string='Start Date', store=True)
    end_date = fields.Date(compute='_compute_end_date', string='End Date', store=True)
