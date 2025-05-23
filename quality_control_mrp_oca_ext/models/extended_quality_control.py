# Copyright 2024 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class JvvQualityControlVerificationType(models.Model):
    _name = "extended.quality.control.verification.type"
    _description = "Verification types for production control"
    _order = "name"

    name = fields.Char(string="Description", required=True)


class JvvQualityControlPackaging(models.Model):
    _name = "extended.quality.control.packaging"
    _description = "Packagings for production control"
    _order = "name"

    name = fields.Char(string="Description", required=True)


class JvvQualityControlComponent(models.Model):
    _name = "extended.quality.control.component"
    _description = "Components for production control"
    _order = "name"

    name = fields.Char(string="Description", required=True)


class JvvQualityControlSolution(models.Model):
    _name = "extended.quality.control.solution"
    _description = "Solutions for production control"
    _order = "name"

    name = fields.Char(string="Description", required=True)


class JvvQualityControl(models.Model):
    _name = "extended.quality.control"
    _description = "Production control"

    mrp_production_id = fields.Many2one(
        string="Manufacturing order", comodel_name="mrp.production"
    )
    mrp_product_id = fields.Many2one(
        string="Product to produce",
        comodel_name="product.product",
        related="mrp_production_id.product_id",
        store=True,
    )
    verification_type_id = fields.Many2one(
        string="Operation", comodel_name="extended.quality.control.verification.type"
    )
    packaging_id = fields.Many2one(
        string="Failure type", comodel_name="extended.quality.control.packaging"
    )
    lot_id = fields.Many2one(string="lot", comodel_name="stock.lot")
    quantity_produced = fields.Float(
        string="quantity produced", default=0.0, digits="Product Unit of Measure"
    )
    operators_lines_ids = fields.One2many(
        string="Operators lines",
        comodel_name="extended.quality.control.line",
        inverse_name="extended_quality_control_id",
    )


class JvvQualityControlLine(models.Model):
    _name = "extended.quality.control.line"
    _description = "Production control lines"

    @api.depends("start_hour", "final_hour")
    def _compute_total_time(self):
        for line in self.filtered(lambda x: x.start_hour and x.final_hour):
            if line.final_hour > line.start_hour:
                line.total_time = line.final_hour - line.start_hour

    extended_quality_control_id = fields.Many2one(
        string="Production control", comodel_name="extended.quality.control"
    )
    operator_id = fields.Many2one(string="Operator", comodel_name="res.users")
    component_id = fields.Many2one(
        string="Component", comodel_name="extended.quality.control.component"
    )
    solution_id = fields.Many2one(
        string="Solution", comodel_name="extended.quality.control.solution"
    )
    control_date = fields.Date(string="Date")
    start_hour = fields.Float(string="Start hour")
    final_hour = fields.Float(string="Final hour")
    total_time = fields.Float(
        string="Total time", compute="_compute_total_time", store=True
    )
    cause = fields.Char(string="Cause detected")
    quantity = fields.Float(default=0.0, digits="Product Unit of Measure")
