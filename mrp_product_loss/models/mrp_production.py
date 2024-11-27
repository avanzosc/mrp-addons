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
