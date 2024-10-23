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

    @api.depends(
        "move_raw_ids",
        "move_raw_ids.estimated_material_cost_to_consume",
        "move_raw_ids.estimated_scrap_cost",
        "workorder_ids",
        "workorder_ids.workorder_cost_estimated",
    )
    def _compute_estimated_scrap_cost(self):
        result = super()._compute_estimated_cost()
        for production in self:
            estimated_scrap_cost = 0
            if production.move_raw_ids:
                estimated_scrap_cost = sum(
                    production.mapped("move_raw_ids.estimated_scrap_cost")
                )
            production.estimated_scrap_cost = estimated_scrap_cost
            production.cost_manufacturing_estimated += estimated_scrap_cost
        return result

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

    def update_prodution_cost(self):
        result = super().update_prodution_cost()
        price_unit_cost = 0
        real_manufacturing_cost = (
            self.cost_workorder_real + self.real_material_cost + self.real_scrap_cost
        )
        if real_manufacturing_cost and self.move_finished_ids:
            for move in self.move_finished_ids:
                if move.quantity_done > 0:
                    move.price_unit_cost = real_manufacturing_cost / move.quantity_done
        if real_manufacturing_cost and self.qty_producing:
            price_unit_cost = real_manufacturing_cost / self.qty_producing
        self.real_manufacturing_cost = real_manufacturing_cost
        self.price_unit_cost = price_unit_cost
        if self.lot_producing_id:
            self.lot_producing_id.with_context(from_production=True).purchase_price = (
                price_unit_cost
            )
        return result
