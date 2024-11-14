# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_scrap(self):
        self.ensure_one()
        result = super().button_scrap()
        result["context"]["product_ids"] = (
            self.move_raw_ids.filtered(lambda x: x.state not in ("done", "cancel"))
            .mapped("product_id")
            .ids
        )
        return result
