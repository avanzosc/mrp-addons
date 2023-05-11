# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        values = super(StockMove, self)._prepare_procurement_values()
        if self.sale_line_id:
            values["sale_line_id"] = self.sale_line_id.id
        return values
