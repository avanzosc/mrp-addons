# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        self._validate_consumption()
        return super().button_mark_done()

    def _validate_consumption(self):
        for production in self:
            for move in production.move_raw_ids:
                qty_done = float_round(move.quantity_done, precision_digits=2)
                should_consume = float_round(
                    move.should_consume_qty, precision_digits=2
                )
                if qty_done != should_consume:
                    error = _(
                        "You must consume what is planned for the product: %(product_name)s"
                    ) % {
                        "product_name": move.product_id.name,
                    }
                    raise UserError(error)
