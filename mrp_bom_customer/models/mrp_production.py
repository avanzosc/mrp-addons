# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model_create_multi
    def create(self, vals_list):
        productions = super(MrpProduction, self).create(vals_list)
        for production in productions:
            production._recompute_bom()
        return productions

    def _recompute_bom(self):
        bom = False
        if not self.origin:
            bom = self._search_bom_for_recompute()
        if self.origin:
            cond = [("name", "=", self.origin)]
            sale = self.env["sale.order"].search(cond, limit=1)
            if sale:
                bom = self._search_bom_for_recompute(sale.partner_id)
                if not bom:
                    bom = self._search_bom_for_recompute()
            else:
                bom = self._search_bom_for_recompute()
        if bom and self.bom_id != bom:
            self.bom_id = bom.id

    def _search_bom_for_recompute(self, customer=False):
        cond = ["|", ("product_id", "=", self.product_id.id),
                ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
                ("company_id", "=", self.company_id.id)]
        if customer:
            cond.append(("customer_id", "=", customer.id))
        bom = self.env["mrp.bom"].search(cond, limit=1)
        return bom
