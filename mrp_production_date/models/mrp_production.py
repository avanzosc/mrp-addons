# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    production_date = fields.Datetime()

    def button_mark_done(self):
        result = super().button_mark_done()
        for production in self:
            if production.production_date:
                moves = self.env["stock.move"].search(
                    [
                        "|",
                        ("production_id", "=", production.id),
                        ("raw_material_production_id", "=", production.id),
                    ]
                )
                moves.write({"date": production.production_date})
                moves.move_line_ids.write({"date": production.production_date})
                production.write({"date_finished": production.production_date})
        return result
