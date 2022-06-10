# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_deconstruction = fields.Boolean(
        string="Is Deconstruction?",
        related="bom_id.is_deconstruction",
        store=True)
    move_line_ids = fields.One2many(
        string="Move Lines",
        comodel_name="stock.move.line",
        inverse_name="production_id")

    @api.constrains("move_raw_ids", "bom_id", "bom_id.is_deconstruction")
    def _check_is_deconstruction(self):
        for production in self:
            if production.bom_id and (
                production.is_deconstruction) is True and (
                    production.move_raw_ids):
                origin = self.move_raw_ids.location_id
                dest = self.move_raw_ids.location_dest_id
                for line in self.move_raw_ids:
                    line.write({
                        "location_id": dest.id,
                        "location_dest_id": origin.id})
                self.write({
                    "location_dest_id": dest.id,
                    "location_src_id": dest.id})

    def button_mark_done(self):
        result = super(MrpProduction, self).button_mark_done()
        if self.is_deconstruction is True:
            origin = self.finished_move_line_ids.location_id
            dest = self.finished_move_line_ids.location_dest_id
            self.finished_move_line_ids.write({
                "location_id": dest.id,
                "location_dest_id": origin.id})
        return result
