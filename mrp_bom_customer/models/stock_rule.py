# Copyright 2024 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_matching_bom(self, product_id, company_id, values):
        procurement_group = values.get("group_id", False)
        partner = procurement_group.partner_id if procurement_group else False
        return super(
            StockRule,
            self.with_context(default_partner_id=partner and partner.id),
        )._get_matching_bom(product_id, company_id, values)
