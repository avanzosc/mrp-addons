# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_manufacturable = fields.Boolean(
        string="Is Manufacturable",
        compute="_compute_manufacturable",
        store=True,
        compute_sudo=True,
    )

    @api.depends("route_ids", "bom_ids", "variant_bom_ids", "bom_ids.type",
                 "variant_bom_ids.type")
    def _compute_manufacturable(self):
        manufacture = self.env.ref("mrp.route_warehouse0_manufacture")
        for product in self:
            manufacture_route = (manufacture in product.route_ids)
            manufacture_bom = any(
                product.variant_bom_ids.filtered(
                    lambda l: l.type == "normal") |
                product.bom_ids.filtered(
                    lambda l: l.type == "normal"))
            product.is_manufacturable = manufacture_route and manufacture_bom
