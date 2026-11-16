# Copyright 2026 AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_configurable_product = fields.Boolean(
        related="product_tmpl_id.has_configurable_attributes"
    )
    configurator_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        compute="_compute_configurator_pricelist_id",
        compute_sudo=True,
    )
    configurator_currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_configurator_pricelist_id",
        compute_sudo=True,
    )

    @api.depends("company_id")
    def _compute_configurator_pricelist_id(self):
        pricelist_obj = self.env["product.pricelist"]
        for production in self:
            configurator_pricelist = pricelist_obj.search(
                [("company_id", "=", production.company_id.id)], limit=1
            )
            if not configurator_pricelist:
                configurator_pricelist = pricelist_obj.search(
                    [("company_id", "=", False)], limit=1
                )
            production.update(
                {
                    "configurator_pricelist_id": configurator_pricelist.id,
                    "configurator_currency_id": configurator_pricelist.currency_id.id,
                }
            )
