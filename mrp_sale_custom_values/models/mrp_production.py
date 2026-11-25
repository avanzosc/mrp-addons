# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from markupsafe import Markup

from odoo import api, fields, models

CUSTOM_VALUE_LABELS = {
    "top graphic": "Top Graphic",
    "bottom graphic": "Bottom Graphic",
    "bottom transfer": "Bottom Graphic",
    "top laser": "Top Laser",
    "bottom laser": "Bottom Laser",
    "sticker oem": "Sticker OEM",
    "warranty oem": "Warranty OEM",
}

GRAPHIC_ATTRIBUTE_LABELS = {
    "top graphic": "Top Graphic",
    "bottom graphic": "Bottom Graphic",
    "bottom transfer": "Bottom Graphic",
}


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_custom_description = fields.Html(
        string="Custom Description",
        compute="_compute_sale_custom_description",
    )

    def _get_sale_order_line(self):
        self.ensure_one()
        return (self.sale_line_id | self.move_dest_ids.sale_line_id)[:1]

    def _get_sale_custom_values_by_label(self):
        self.ensure_one()
        custom_values_by_label = dict.fromkeys(CUSTOM_VALUE_LABELS.values())
        sale_line = self._get_sale_order_line()
        for custom_value in sale_line.product_custom_attribute_value_ids:
            attribute = (
                custom_value.custom_product_template_attribute_value_id.attribute_id
            )
            attribute_name = (attribute.name or "").strip().casefold()
            label = CUSTOM_VALUE_LABELS.get(attribute_name)
            if label:
                custom_values_by_label[label] = custom_value.custom_value
        return custom_values_by_label

    def _get_graphic_component_description(self, bom_line):
        self.ensure_one()
        if not bom_line:
            return False
        custom_values_by_label = self._get_sale_custom_values_by_label()
        attributes = bom_line.bom_product_template_attribute_value_ids.attribute_id
        for attribute in attributes:
            label = GRAPHIC_ATTRIBUTE_LABELS.get(
                (attribute.name or "").strip().casefold()
            )
            custom_value = label and custom_values_by_label.get(label)
            if custom_value:
                return f"{label}: {custom_value}"
        return False

    @api.depends(
        "move_dest_ids.sale_line_id.product_custom_attribute_value_ids.custom_value",
        "move_dest_ids.sale_line_id.product_custom_attribute_value_ids."
        "custom_product_template_attribute_value_id.attribute_id.name",
        "sale_line_id.product_custom_attribute_value_ids.custom_value",
        "sale_line_id.product_custom_attribute_value_ids."
        "custom_product_template_attribute_value_id.attribute_id.name",
    )
    def _compute_sale_custom_description(self):
        for production in self:
            custom_values_by_label = production._get_sale_custom_values_by_label()
            description_lines = [
                Markup("<strong>%s:</strong> %s") % (label, custom_value)
                for label, custom_value in custom_values_by_label.items()
                if custom_value
            ]
            production.sale_custom_description = Markup("<br/>").join(description_lines)
