# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model_create_multi
    def create(self, vals_list):
        productions = super(MrpProduction, self).create(vals_list)
        for production in productions:
            if production.origin:
                cond = [("name", "=", production.origin)]
                sale = self.env["sale.order"].search(cond, limit=1)
                if sale:
                    production._recompute_bom(sale.partner_id)
        return productions

    def _recompute_bom(self, customer):
        bom_obj = self.env["mrp.bom"]
        cond = ["|", ("product_id", "=", self.product_id.id),
                ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
                ("customer_id", "=", customer.id),
                ("company_id", "=", self.company_id.id)]
        bom = bom_obj.search(cond, limit=1)
        self.bom_id = bom.id if bom else False
