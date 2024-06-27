# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_default_location_id(self):
        if "production_id" in self.env.context:
            production = self.env.context["production_id"]
            production = self.env["mrp.production"].search(
                [("id", "=", production)], limit=1
            )
            result = production.picking_type_id.default_location_src_id.id
            if production.is_deconstruction is True:
                result = production.location_src_id.id
            return result

    def _get_default_location_dest_id(self):
        if "production_id" in self.env.context:
            production = self.env.context["production_id"]
            production = self.env["mrp.production"].search(
                [("id", "=", production)], limit=1
            )
            result = production.production_location_id.id
            if production.is_deconstruction is True:
                result = production.picking_type_id.default_location_src_id.id
            return result

    location_id = fields.Many2one(default=_get_default_location_id)
    location_dest_id = fields.Many2one(default=_get_default_location_dest_id)

    @api.onchange("location_id", "location_dest_id")
    def onchange_product_id_domain(self):
        domain = {}
        if "production_id" in self.env.context:
            production = self.env.context["production_id"]
            production = self.env["mrp.production"].search(
                [("id", "=", production)], limit=1
            )
            domain = {}
            if production.is_deconstruction is not True and (production.move_raw_ids):
                products = production.move_raw_ids.mapped("product_id")
                domain = {"domain": {"product_id": [("id", "in", products.ids)]}}
        elif "default_production_id" in self.env.context:
            production = self.env.context["default_production_id"]
            production = self.env["mrp.production"].search(
                [("id", "=", production)], limit=1
            )
            domain = {}
            if production.move_byproduct_ids:
                products = production.move_byproduct_ids.mapped("product_id")
                domain = {"domain": {"product_id": [("id", "in", products.ids)]}}
        return domain
