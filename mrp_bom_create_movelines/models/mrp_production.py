# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def action_confirm(self):
        super(MrpProduction, self).action_confirm()
        self.filtered(
            lambda p: p.bom_id
            and p.bom_id.category_id
            and p.bom_id.category_id.bring_components_on_confirm
        )._bring_components_to_inputs()

    def _bring_components_to_inputs(self):
        for production in self:
            for move in production.move_raw_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
                and m.product_id.type == "product"
                and not m.move_line_ids
            ):
                self.env["stock.move.line"].create(
                    {
                        "move_id": move.id,
                        "product_id": move.product_id.id,
                        "product_uom_id": move.product_uom.id,
                        "product_uom_qty": 0,
                        "qty_done": 0,
                        "location_id": move.location_id.id,
                        "location_dest_id": move.location_dest_id.id,
                        "company_id": production.company_id.id,
                        "production_id": production.id,
                    }
                )
