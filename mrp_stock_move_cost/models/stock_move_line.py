# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, vals):
        found = False
        if "lot_id" in vals or "qty_done" in vals:
            found = True
        result = super(StockMoveLine, self).write(vals)
        if found:
            self._put_price_unit_cost_in_move_lines()
            if self.production_id and self.production_id.state == "done":
                self.production_id.put_cost_in_move_lines()
        if (not found and self.move_id.raw_material_production_id and
                self.move_id.raw_material_production_id.state == "done"):
            self.move_id.raw_material_production_id.put_cost_in_move_lines()
        return result

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
            production.put_cost_in_move_lines()
        return result
