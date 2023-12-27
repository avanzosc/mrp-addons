# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_deconstruction = fields.Boolean(
        string="Is Deconstruction?",
        related="bom_id.is_deconstruction",
        store=True)
    move_line_ids = fields.One2many(
        string="Move Lines",
        comodel_name="stock.move.line",
        inverse_name="production_id",
        domain=lambda self: [
            ("location_dest_id", "in", self.production_location_id.ids)],
        )
    finished_move_line_ids = fields.One2many(
        compute=False,
        inverse_name="production_id",
        domain=lambda self: [
            ("location_id", "in", self.production_location_id.ids),
            ("location_dest_id", "in", self.location_dest_id.ids)]
        )

    @api.depends('product_id', 'company_id', "is_deconstruction")
    def _compute_production_location(self):
        super(MrpProduction, self)._compute_production_location()
        for production in self:
            if production.is_deconstruction:
                production.production_location_id = (
                    production.picking_type_id.default_location_src_id.id) or (
                        False)

    def write(self, vals):
        res = super(MrpProduction, self).write(vals)
        if "move_finished_ids" in vals:
            for line in self:
                if line.is_deconstruction and line.move_finished_ids:
                    for move in line.move_finished_ids:
                        move.location_id = line.production_location_id.id
                        move.location_dest_id = line.location_src_id.id
        return res

    @api.constrains("bom_id", "is_deconstruction")
    def _check_is_deconstruction(self):
        for production in self:
            if production.bom_id and (
                production.is_deconstruction) is True and (
                    production.move_raw_ids):
                origin = production.picking_type_id.default_location_src_id
                if origin.usage != "internal" and (
                    production.production_location_id.usage) == (
                        "internal"):
                    origin = production.production_location_id
                dest = production.move_raw_ids.location_dest_id
                if dest.usage == "production":
                    production.write({
                        "location_dest_id": dest.id,
                        "location_src_id": dest.id,
                        "production_location_id": origin.id})
                    for move in production.move_raw_ids:
                        move.write({
                            "location_id": dest.id,
                            "location_dest_id": origin.id})
                        for line in move.move_line_ids:
                            line.write({
                                "location_id": dest.id,
                                "location_dest_id": origin.id})

    def action_confirm(self):
        self._check_is_deconstruction()
        return super(MrpProduction, self).action_confirm()

    def button_mark_done(self):
        result = super(MrpProduction, self).button_mark_done()
        for production in self:
            if production.is_deconstruction is True:
                origin = production.finished_move_line_ids.location_id
                dest = production.finished_move_line_ids.location_dest_id
                production.finished_move_line_ids.write({
                    "location_id": dest.id,
                    "location_dest_id": origin.id})
        return result
