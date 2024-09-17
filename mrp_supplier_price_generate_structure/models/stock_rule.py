# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.multi
    def _make_po_select_supplier(self, values, suppliers):
        partner_id = values.get('partner_id')
        if partner_id:
            return suppliers.filtered(lambda x: x.name.id == partner_id)[0]
        return super()._make_po_select_supplier(values, suppliers)
