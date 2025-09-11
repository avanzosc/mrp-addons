# Copyright 2025 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    emptying_type_id = fields.Many2one(comodel_name="stock.picking.type")
    emptying_pickings_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="emptying_production_id",
    )
    count_emptying_pickings = fields.Integer(compute="_compute_count_emptying_pickings")

    @api.depends("emptying_pickings_ids")
    def _compute_count_emptying_pickings(self):
        for production in self:
            count = 0
            if production.emptying_pickings_ids:
                count = len(production.emptying_pickings_ids)
            production.count_emptying_pickings = count

    def action_view_emptying_picking(self):
        context = self.env.context.copy()
        return {
            "name": _("Emptying Picking"),
            "view_mode": "tree,form",
            "res_model": "stock.picking",
            "domain": [("id", "in", self.emptying_pickings_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context,
        }

    def emptying_lots_in_location(self):
        for production in self:
            if not production.emptying_type_id:
                raise ValidationError(_("You muts introduce the emptying picking."))
            else:
                if production.emptying_pickings_ids and any(
                    [
                        p.state not in ("done", "cancel")
                        for p in production.emptying_pickings_ids
                    ]
                ):
                    picking = production.emptying_pickings_ids.filtered(
                        lambda c: c.state not in ("done", "cancel")
                    )[:1]
                    for line in picking.move_line_ids_without_package:
                        line.unlink()
                    for move in picking.move_ids_without_package:
                        move.unlink()
                else:
                    picking = self.env["stock.picking"].create(
                        {
                            "emptying_production_id": production.id,
                            "picking_type_id": production.emptying_type_id.id,
                            "location_id": (
                                production.emptying_type_id.default_location_src_id.id
                            ),
                            "location_dest_id": (
                                production.emptying_type_id.default_location_dest_id.id
                            ),
                        }
                    )
                for line in production.move_line_ids:
                    self.env["stock.move.line"].create_emptying_lots_movelines(
                        line=line, picking=picking
                    )
                picking.action_confirm()
