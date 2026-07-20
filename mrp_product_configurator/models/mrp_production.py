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
        related="configurator_pricelist_id.currency_id"
    )

    @api.depends("company_id")
    def _compute_configurator_pricelist_id(self):
        Pricelist = self.env["product.pricelist"]
        for production in self:
            production.configurator_pricelist_id = Pricelist.search(
                [
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "=", production.company_id.id),
                ],
                order="company_id desc, id",
                limit=1,
            )
