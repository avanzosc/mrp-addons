# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    price_unit_cost = fields.Float(
        string="Cost Unit Price", digits="Product Price", copy=False
    )
    cost = fields.Float(digits="Product Price", copy=False)

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
        cost = 0
        if self.move_raw_ids:
            cost = sum(self.move_raw_ids.mapped("cost"))
        if cost and self.move_finished_ids:
            for move in self.move_finished_ids:
                if move.quantity_done > 0:
                    move.price_unit_cost = cost / move.quantity_done
        self.cost = cost
        if cost and self.qty_producing:
            price_unit_cost = cost / self.qty_producing
        self.price_unit_cost = price_unit_cost
        if self.lot_producing_id:
            self.lot_producing_id.with_context(from_production=True).purchase_price = (
                price_unit_cost
            )
