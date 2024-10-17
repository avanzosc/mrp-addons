# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # scapt costs
    estimated_scrap_cost = fields.Float(
        copy=False,
        store=True,
        compute="_compute_estimated_scrap_cost",
    )
    real_scrap_cost = fields.Float(
        copy=False,
        store=True,
        compute="_compute_real_scrap_cost",
    )

    @api.depends("move_raw_ids", "move_raw_ids.estimated_scrap_cost")
    def _compute_estimated_scrap_cost(self):
        for production in self:
            estimated_scrap_cost = 0
            if production.move_raw_ids:
                estimated_scrap_cost = sum(
                    production.mapped("move_raw_ids.estimated_scrap_cost")
                )
            production.estimated_scrap_cost = estimated_scrap_cost

    @api.depends("move_raw_ids", "move_raw_ids.state", "move_raw_ids.real_scrap_cost")
    def _compute_real_scrap_cost(self):
        for production in self:
            real_scrap_cost = 0
            moves = production.move_raw_ids.filtered(
                lambda x: x.state not in ("draft", "cancel")
            )
            if moves:
                real_scrap_cost = sum(moves.mapped("real_scrap_cost"))
            production.real_scrap_cost = real_scrap_cost

    @api.depends(
        "cost_material_to_consume", "cost_workorder_estimated", "estimated_scrap_cost"
    )
    def _compute_cost_manufacturing_estimated(self):
        result = super()._compute_cost_manufacturing_estimated()
        for production in self:
            production.cost_manufacturing_estimated = (
                production.cost_material_to_consume
                + production.cost_workorder_estimated
                + production.estimated_scrap_cost
            )
        return result

    @api.depends("cost_material_consumed", "cost_workorder_real", "real_scrap_cost")
    def _compute_cost_manufacturing_real(self):
        result = super()._compute_cost_manufacturing_real()
        for production in self:
            production.cost_manufacturing_real = (
                production.cost_material_consumed
                + production.cost_workorder_real
                + production.real_scrap_cost
            )
        return result

    def _catch_cost_to_update_finished_move_cost_and_lot(self):
        cost = super()._catch_cost_to_update_finished_move_cost_and_lot()
        cost += self.real_scrap_cost
        return cost
