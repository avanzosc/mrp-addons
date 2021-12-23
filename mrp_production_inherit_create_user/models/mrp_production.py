# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        res = super()._prepare_mo_vals(product_id, product_qty, product_uom,
                                       location_id, name, origin, values, bom)
        res['user_id'] = self.env.user.id
        return res