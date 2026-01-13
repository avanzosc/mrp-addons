from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    operator_id = fields.Many2one(
        comodel_name="res.users",
        string="Operator",
        related="create_uid",
        store=True,
        index=True,
        readonly=True,
    )

    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Shift (Calendar)",
        related="workcenter_id.resource_calendar_id",
        store=True,
        index=True,
        readonly=True,
    )

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacturing Order",
        related="workorder_id.production_id",
        store=True,
        index=True,
        readonly=True,
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        related="production_id.product_id",
        store=True,
        index=True,
        readonly=True,
    )

    procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        related="production_id.procurement_group_id",
        store=True,
        index=True,
        readonly=True,
    )

    date = fields.Date(
        compute="_compute_date",
        store=True,
        index=True,
    )

    time_hours = fields.Float(
        string="Time (h)",
        compute="_compute_time_hours",
        store=True,
        group_operator="sum",
    )

    plates_done = fields.Float(
        string="Plates Produced",
        related="workorder_id.qty_produced",
        store=True,
        group_operator="sum",
        readonly=True,
    )

    speed = fields.Float(
        string="Speed (plates/h)",
        compute="_compute_speed",
        store=True,
        group_operator="avg",
    )

    @api.depends("date_start")
    def _compute_date(self):
        for rec in self:
            rec.date = fields.Date.to_date(rec.date_start) if rec.date_start else False

    @api.depends("duration")
    def _compute_time_hours(self):
        for rec in self:
            rec.time_hours = (rec.duration or 0.0) / 60.0

    @api.depends("time_hours", "plates_done")
    def _compute_speed(self):
        for rec in self:
            rec.speed = (
                (rec.plates_done or 0.0) / rec.time_hours if rec.time_hours else 0.0
            )
