# Copyright 2020 Alfredo de la Fuente - Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.multi
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, values, po, partner
    ):
        values = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner
        )
        if self.env.context.get("analytic_account_id", False):
            values["account_analytic_id"] = self.env.context.get("analytic_account_id")
        return values

    @api.multi
    def _run_manufacture(
        self, product_id, product_qty, product_uom, location_id, name, origin, values
    ):
        production = self.env["mrp.production"]
        production_sudo = production.sudo().with_context(
            force_company=values["company_id"].id
        )
        production = production_sudo.browse(
            self.env.context.get("procurement_production_id")
        )
        if (
            not production
            or not production.product_line_ids.mapped("new_production_id")
            or self._context.get("force_execution")
        ):
            super()._run_manufacture(
                product_id, product_qty, product_uom, location_id, name, origin, values
            )
        elif production.product_line_ids.mapped("new_production_id"):
            return True
