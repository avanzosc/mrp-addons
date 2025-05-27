# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        result = super().action_confirm()
        for production in self:
            lines = production.move_raw_ids.filtered(
                lambda x: x.product_tmpl_id.product_loss_qty > 0
            )
            for line in lines:
                loss_qty = line.product_tmpl_id.product_loss_qty
                line.write(
                    {
                        "product_loss_qty": loss_qty,
                    }
                )
        return result

    def write(self, vals):
        if (
            len(self) == 1
            and isinstance(vals, dict)
            and "qty_producing" in vals
            and vals.get("qty_producing", 0) > 0
            and "move_raw_ids" in vals
            and vals.get("move_raw_ids", [])
        ):
            for raw in vals.get("move_raw_ids"):
                if (
                    len(raw) == 3
                    and isinstance(raw[0], int)
                    and raw[0] == 1
                    and isinstance(raw[1], int)
                    and isinstance(raw[2], dict)
                ):
                    move = self.env["stock.move"].browse(raw[1])
                    if move.bom_line_id and move.product_id.product_loss_qty:
                        raw[2]["to_consume_before_loss_qty"] = (
                            move.bom_line_id.product_qty * vals.get("qty_producing")
                        )
        return super().write(vals)
