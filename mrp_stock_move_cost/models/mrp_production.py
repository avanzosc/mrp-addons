# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    price_unit_cost = fields.Float(
        string="Cost Unit Price", digits="Product Price", copy=False
    )
    cost = fields.Float(
        string="Cost", digits="Product Price", copy=False
    )

    @api.depends("state")
    def _compute_price_unit_cost(self):
        for production in self:
            cost = 0
            price_unit = 0
            if production.state == "done" and production.finished_move_line_ids:
                cost = sum(production.finished_move_line_ids.mapped("cost"))
                production.cost = cost
                lines = production.finished_move_line_ids.filtered(
                    lambda x: x.qty_done > 0)
                if lines:
                    qty_done = sum(lines.mapped("qty_done"))
                    if cost > 0 and qty_done > 0:
                        price_unit = cost / qty_done
            production.cost = cost
            production.price_unit_cost = price_unit
        
    def button_mark_done(self):
        action = super(MrpProduction, self).button_mark_done()
        for production in self.filtered(lambda x: x.state == "done"):
            production.put_cost_in_move_lines()
        return action

    def _put_cost_in_mrp_production(self):
        productions = self.filtered(lambda x: x.state == "done")
        for production in productions:
            production.put_cost_in_move_lines()

    def put_cost_in_move_lines(self):
        production_cost = 0
        production_qty_done = 0
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
                purchase_price = 0
                if produce_line.qty_done > 0:
                    production_qty_done += produce_line.qty_done
                    purchase_price = cost / produce_line.qty_done
                vals = {}
                production_cost += cost
                if produce_line.cost != cost:
                    vals["cost"] = cost
                if produce_line.price_unit_cost != purchase_price:
                    vals["price_unit_cost"] = purchase_price
                if vals:
                    produce_line.write(vals)
        self.cost = production_cost
        if production_cost and production_qty_done:
            price_unit_cost = production_cost / production_qty_done
        else:
            price_unit_cost = 0
        self.price_unit_cost = price_unit_cost
        if (self.lot_producing_id and
                self.lot_producing_id.purchase_price != price_unit_cost):
            self.lot_producing_id.purchase_price = price_unit_cost
