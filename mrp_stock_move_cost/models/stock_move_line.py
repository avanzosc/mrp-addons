# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def unlink(self):
        productions = self.env["mrp.production"]
        for line in self.filtered(lambda x: x.production_id):
            if line.production_id not in productions:
                productions += line.production_id
        for line in self.filtered(
                lambda x: x.move_id and x.move_id.raw_material_production_id):
            if line.move_id.raw_material_production_id not in productions:
                productions += line.move_id.raw_material_production_id
        result = super(StockMoveLine, self).unlink()
        for production in productions:
            production.update_prodution_cost()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(StockMoveLine, self).create(vals_list)
        done_lines = lines.filtered(lambda x: x.state == "done")
        if done_lines:
            done_lines.search_production_and_update()
        return lines

    def write(self, vals):
        result = super(StockMoveLine, self).write(vals)
        if self and "qty_done" in vals and self.state == "done":
            self.search_production_and_update()
        return result

    def search_production_and_update(self):
        for line in self:
            production = self.env["mrp.production"]
            if line.production_id:
                production = line.production_id
            if line.move_id and line.move_id.raw_material_production_id:
                production = line.move_id.raw_material_production_id
            if production and production.state == "done":
                production.update_prodution_cost()
