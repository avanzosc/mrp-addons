# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        self._validate_consumption()
        return super().button_mark_done()

    def _validate_consumption(self):
        for production in self:
            for move in production.move_raw_ids:
                if move.quantity_done < move.should_consume_qty:
                    error = _(
                        "You must consume what is planned for the product: %(product_name)s"
                    ) % {
                        "product_name": move.product_id.name,
                    }
                    raise UserError(error)
                if move.quantity_done > move.should_consume_qty:
                    error = _(
                        "You cannot consume more than planned for the product: %(product_name)s"
                    ) % {
                        "product_name": move.product_id.name,
                    }
                    raise UserError(error)
