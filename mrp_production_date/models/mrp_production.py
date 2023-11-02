# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    production_date = fields.Datetime(
        string="Production Date",
    )

    def button_mark_done(self):
        result = super(MrpProduction, self).button_mark_done()
        for production in self:
            if production.production_date:
                moves = self.env["stock.move"].search(
                    ['|',
                     ("production_id", "=", production.id),
                     ("raw_material_production_id", "=", production.id)])
                for move in moves:
                    move.date = production.production_date
                    for line in move.move_line_ids:
                        line.date = production.production_date
                production.date_finished = production.production_date
        return result
