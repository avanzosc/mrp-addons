# Copyright 2022 Patxi Lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # Material costs
    estimated_material_cost = fields.Float(
        copy=False,
        store=True,
        compute="_compute_estimated_cost",
    )
    real_material_cost = fields.Float(
        copy=False,
    )
    # Workorder costs
    cost_workorder_estimated = fields.Float(
        string="Estimated Work Cost",
        copy=False,
        store=True,
        compute="_compute_estimated_cost",
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
        compute="_compute_cost_workorder_real",
    )

    price_unit_cost = fields.Float(
        string="Cost Unit Price", digits="Product Price", copy=False
    )
    real_manufacturing_cost = fields.Float(digits="Product Price", copy=False)

    @api.depends(
        "move_raw_ids",
        "move_raw_ids.estimated_material_cost_to_consume",
        "workorder_ids",
        "workorder_ids.workorder_cost_estimated",
    )
    def _compute_estimated_cost(self):
        for production in self:
            estimated_material_cost = 0
            cost_workorder_estimated = 0
            if production.move_raw_ids:
                estimated_material_cost = sum(
                    production.mapped("move_raw_ids.estimated_material_cost_to_consume")
                )
            if production.workorder_ids:
                cost_workorder_estimated = sum(
                    production.mapped("workorder_ids.workorder_cost_estimated")
                )
            production.estimated_material_cost = estimated_material_cost
            production.cost_workorder_estimated = cost_workorder_estimated
            production.cost_manufacturing_estimated = (
                estimated_material_cost + cost_workorder_estimated
            )

    @api.depends("state", "workorder_ids.workorder_cost_real")
    def _compute_cost_workorder_real(self):
        for production in self:
            cost_workorder_real = 0
            if production.state == "done":
                cost_workorder_real = sum(
                    production.mapped("workorder_ids.workorder_cost_real")
                )
            production.cost_workorder_real = cost_workorder_real

    def write(self, vals):
        result = super().write(vals)
        if "state" in vals and vals.get("state", False) == "done":
            for production in self:
                production.update_prodution_cost()
        return result

    def _put_cost_in_mrp_production(self):
        productions = self.filtered(lambda x: x.state == "done")
        for production in productions:
            production.update_prodution_cost()

    def update_prodution_cost(self):
        price_unit_cost = 0
        real_material_cost = 0
        if self.move_raw_ids:
            real_material_cost = sum(self.move_raw_ids.mapped("cost"))
        real_manufacturing_cost = self.cost_workorder_real + real_material_cost
        if real_manufacturing_cost and self.move_finished_ids:
            for move in self.move_finished_ids:
                if move.quantity_done > 0:
                    move.price_unit_cost = real_manufacturing_cost / move.quantity_done
        if real_manufacturing_cost and self.qty_producing:
            price_unit_cost = real_manufacturing_cost / self.qty_producing
        self.price_unit_cost = price_unit_cost
        self.real_material_cost = real_material_cost
        self.real_manufacturing_cost = real_manufacturing_cost
        if self.lot_producing_id:
            self.lot_producing_id.with_context(from_production=True).purchase_price = (
                price_unit_cost
            )
