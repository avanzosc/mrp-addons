# Copyright 2022 Patxi Lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # Material costs
    cost_material_to_consume = fields.Float(
        string="Estimated Material Cost",
        copy=False,
        store=True,
        compute="_compute_cost_material_to_consume",
    )
    cost_material_consumed = fields.Float(
        string="Real Material Cost",
        copy=False,
        store=True,
        compute="_compute_cost_material_consumed",
    )
    # Workorder costs
    cost_workorder_estimated = fields.Float(
        string="Estimated Work Cost",
        copy=False,
        store=True,
        compute="_compute_cost_workorder_estimated",
    )
    cost_workorder_real = fields.Float(
        string="Real Work Cost",
        copy=False,
        store=True,
        compute="_compute_cost_workorder_real",
    )
    # Manufacturing costs
    cost_manufacturing_estimated = fields.Float(
        string="Estimated Manufacturing Cost",
        copy=False,
        store=True,
        compute="_compute_cost_manufacturing_estimated",
    )
    cost_manufacturing_real = fields.Float(
        string="Real Manufacturing Cost",
        copy=False,
        store=True,
        compute="_compute_cost_manufacturing_real",
    )

    @api.depends("move_raw_ids.material_cost_to_consume")
    def _compute_cost_material_to_consume(self):
        for production in self:
            production.cost_material_to_consume = sum(
                production.mapped("move_raw_ids.material_cost_to_consume")
            )

    @api.depends("move_raw_ids.material_cost_consumed")
    def _compute_cost_material_consumed(self):
        for production in self:
            production.cost_material_consumed = sum(
                production.mapped("move_raw_ids.material_cost_consumed")
            )

    @api.depends("workorder_ids.workorder_cost_estimated")
    def _compute_cost_workorder_estimated(self):
        for production in self:
            production.cost_workorder_estimated = sum(
                production.mapped("workorder_ids.workorder_cost_estimated")
            )

    @api.depends("workorder_ids.workorder_cost_real")
    def _compute_cost_workorder_real(self):
        for production in self:
            production.cost_workorder_real = sum(
                production.mapped("workorder_ids.workorder_cost_real")
            )

    @api.depends("cost_material_to_consume", "cost_workorder_estimated")
    def _compute_cost_manufacturing_estimated(self):
        for production in self:
            production.cost_manufacturing_estimated = (
                production.cost_material_to_consume
                + production.cost_workorder_estimated
            )

    @api.depends("cost_material_consumed", "cost_workorder_real")
    def _compute_cost_manufacturing_real(self):
        for production in self:
            production.cost_manufacturing_real = (
                production.cost_material_consumed + production.cost_workorder_real
            )
