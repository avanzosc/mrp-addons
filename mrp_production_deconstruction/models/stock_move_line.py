# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_production_from_context(self):
        production_id = self.env.context.get("production_id") or self.env.context.get(
            "default_production_id"
        )
        return (
            self.env["mrp.production"].browse(production_id) if production_id else False
        )

    def _get_default_location_id(self):
        production = self._get_production_from_context()
        if production:
            result = production.picking_type_id.default_location_src_id.id
            if production.is_deconstruction:
                result = production.location_src_id.id
            return result

    def _get_default_location_dest_id(self):
        production = self._get_production_from_context()
        if production:
            result = production.production_location_id.id
            if production.is_deconstruction:
                result = production.picking_type_id.default_location_src_id.id
            return result

    location_id = fields.Many2one(default=_get_default_location_id)
    location_dest_id = fields.Many2one(default=_get_default_location_dest_id)

    @api.onchange("location_id", "location_dest_id")
    def onchange_product_id_domain(self):
        domain = {}
        if "production_id" in self.env.context:
            production = self._get_production_from_context()
            if (
                production
                and not production.is_deconstruction
                and production.move_raw_ids
            ):
                products = production.move_raw_ids.mapped("product_id")
                domain = {"domain": {"product_id": [("id", "in", products.ids)]}}
        elif "default_production_id" in self.env.context:
            production = self._get_production_from_context()
            if production and production.move_byproduct_ids:
                products = production.move_byproduct_ids.mapped("product_id")
                domain = {"domain": {"product_id": [("id", "in", products.ids)]}}
        return domain
