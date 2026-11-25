# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    graphic_custom_description = fields.Char(
        compute="_compute_graphic_custom_description",
    )

    @api.depends(
        "bom_line_id.bom_product_template_attribute_value_ids.attribute_id.name",
        "raw_material_production_id.move_dest_ids.sale_line_id."
        "product_custom_attribute_value_ids.custom_value",
        "raw_material_production_id.sale_line_id."
        "product_custom_attribute_value_ids.custom_value",
    )
    def _compute_graphic_custom_description(self):
        for move in self:
            production = move.raw_material_production_id
            move.graphic_custom_description = (
                production._get_graphic_component_description(move.bom_line_id)
                if production
                else False
            )

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()
        if self.graphic_custom_description:
            values["product_description_variants"] = self.graphic_custom_description
        return values
