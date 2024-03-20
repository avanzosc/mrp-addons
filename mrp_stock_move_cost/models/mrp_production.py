# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    price_unit_cost = fields.Float(
        string="Cost Unit Price", digits="Product Price", copy=False
    )
    cost = fields.Float(
        string="Cost", digits="Product Price", copy=False
    )

    def write(self, vals):
        result = super(MrpProduction, self).write(vals)
        if "state" in vals and vals.get("state", False) == "done":
            for production in self:
                production.update_prodution_cost()
        return result

    def _put_cost_in_mrp_production(self):
        productions = self.filtered(lambda x: x.state == "done")
        for production in productions:
            production.update_prodution_cost()

    def update_prodution_cost(self):
        cond = ["|", ("move_id.raw_material_production_id", "=", self.id),
                ("move_id.production_id", "=", self.id)]
        lines = self.env["stock.move.line"].search(cond)
        if lines:
            consumed_lines = lines.filtered(
                lambda x: x.move_id.raw_material_production_id == self)
            cost = sum(consumed_lines.mapped("cost"))
            produce_lines = lines.filtered(
                lambda x: x.move_id.production_id == self)
            for produce_line in produce_lines:
                price_unit_cost = 0
                if produce_line.qty_done > 0:
                    price_unit_cost = cost / produce_line.qty_done
                produce_line.price_unit_cost = price_unit_cost
        self.cost = cost
        if cost and self.qty_producing:
            price_unit_cost = cost / self.qty_producing
        else:
            price_unit_cost = 0
        self.price_unit_cost = price_unit_cost
        if self.lot_producing_id:
            self.lot_producing_id.with_context(
                from_production=True).purchase_price = price_unit_cost
