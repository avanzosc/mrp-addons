# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("quantity")
    def check_quantity(self):
        if "with_tracking_serial" not in self.env.context:
            return super(StockQuant, self).check_quantity()
