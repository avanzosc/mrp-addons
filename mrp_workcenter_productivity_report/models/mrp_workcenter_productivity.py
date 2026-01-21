from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    calendar_id = fields.Many2one(
        "resource.calendar",
        string="Shift (Calendar)",
        compute="_compute_calendar_id",
        store=True,
        readonly=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        compute="_compute_employee_id",
        store=True,
        readonly=True,
    )
    production_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Order",
        compute="_compute_related",
        store=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        compute="_compute_related",
        store=True,
        readonly=True,
    )
    procurement_group_id = fields.Many2one(
        "procurement.group",
        string="Procurement Group",
        compute="_compute_related",
        store=True,
        readonly=True,
    )

    duration_hours = fields.Float(
        string="Time (hours)",
        compute="_compute_duration_hours",
        store=True,
        readonly=True,
        group_operator="sum",
    )
    plates_done = fields.Float(
        string="Plates fabricated",
        compute="_compute_plates_speed",
        store=True,
        readonly=True,
        group_operator="sum",
    )
    speed = fields.Float(
        string="Average speed",
        compute="_compute_plates_speed",
        store=True,
        readonly=True,
        group_operator="avg",
    )

    @api.depends(
        "workorder_id.workcenter_id.resource_calendar_id",
        "workcenter_id.resource_calendar_id",
    )
    def _compute_calendar_id(self):
        for rec in self:
            wo = rec.workorder_id
            rec.calendar_id = (
                wo.workcenter_id.resource_calendar_id
                if wo and wo.workcenter_id
                else False
            ) or (
                rec.workcenter_id.resource_calendar_id if rec.workcenter_id else False
            )

    @api.depends("user_id", "workorder_id")
    def _compute_employee_id(self):
        Employee = self.env["hr.employee"].sudo()
        for rec in self:
            user = rec.user_id or getattr(rec.workorder_id, "user_id", False)
            rec.employee_id = (
                Employee.search([("user_id", "=", user.id)], limit=1) if user else False
            )

    @api.depends("workorder_id")
    def _compute_related(self):
        for rec in self:
            wo = rec.workorder_id
            mo = wo.production_id if wo and hasattr(wo, "production_id") else False
            rec.production_id = mo
            rec.product_id = getattr(wo, "product_id", False) or (
                mo.product_id if mo else False
            )
            rec.procurement_group_id = mo.procurement_group_id if mo else False

    @api.depends("duration")
    def _compute_duration_hours(self):
        for rec in self:
            rec.duration_hours = (rec.duration or 0.0) / 60.0

    @api.depends("workorder_id", "duration_hours")
    def _compute_plates_speed(self):
        candidates = (
            "qty_produced",
            "qty_done",
            "produced_qty",
            "qty_production",
            "qty_producing",
        )
        for rec in self:
            wo = rec.workorder_id
            qty = 0.0
            if wo:
                for f in candidates:
                    if hasattr(wo, f):
                        qty = float(getattr(wo, f) or 0.0)
                        break
            rec.plates_done = qty
            rec.speed = qty / rec.duration_hours if rec.duration_hours else 0.0
