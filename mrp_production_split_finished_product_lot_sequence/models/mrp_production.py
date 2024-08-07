# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_generate_serial(self):
        return super(
            MrpProduction, self.with_context(from_product_lot_sequence=True)
        ).action_generate_serial()

    def _prepare_stock_lot_values(self):
        self.ensure_one()
        return super(
            MrpProduction, self.with_context(from_product_lot_sequence=True)
        )._prepare_stock_lot_values()

    def button_mark_done(self):
        return super(
            MrpProduction,
            self.with_context(
                from_product_lot_sequence=True, from_button_mark_done=True
            ),
        ).button_mark_done()
