# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    reader = fields.Char(copy=False)

    @api.onchange("reader")
    def onchange_reader(self):
        result = super().onchange_reader()
        if (
            self.reader
            and self.product_id
            and "from_mrp_production" in self.env.context
            and self.env.context.get("from_mrp_production", False)
        ):
            stock_move = self.production_id.move_raw_ids.filtered(
                lambda x: x.product_id == self.product_id
            )
            if not stock_move:
                message = _("Reader product: %(product)s, not found in operations.") % {
                    "product": self.product_id.name,
                }
                raise ValidationError(message)
            self.move_id = stock_move.id
        return result
