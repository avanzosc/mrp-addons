# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    match_on_attribute_ids = fields.Many2many(readonly=False)
    component_match_attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Component Match Attribute",
    )
    component_attribute_ids = fields.Many2many(
        comodel_name="product.attribute",
        compute="_compute_component_attribute_ids",
        string="Component Attributes",
    )

    @api.depends("component_template_id")
    def _compute_component_attribute_ids(self):
        for line in self:
            line.component_attribute_ids = (
                line.component_template_id.attribute_line_ids.attribute_id.filtered(
                    lambda attribute: attribute.create_variant != "no_variant"
                )
            )

    def _get_match_on_attribute_ids(self):
        self.ensure_one()
        if self.match_on_attribute_ids:
            return self.match_on_attribute_ids
        if not self.component_template_id:
            return self.env["product.attribute"]
        return self.component_template_id.attribute_line_ids.attribute_id.filtered(
            lambda attribute: attribute.create_variant != "no_variant"
        )

    def _check_component_attributes(self):
        return True


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _get_component_template_product(
        self, bom_line, bom_product_id, line_product_id
    ):
        if not bom_line.component_template_id:
            return line_product_id

        component_template = bom_line.component_template_id
        match_attributes = bom_line._get_match_on_attribute_ids()
        if not match_attributes:
            return False

        combination = self.env["product.template.attribute.value"]
        for ptav in bom_product_id.product_template_attribute_value_ids.filtered(
            lambda value: value.attribute_id in match_attributes
        ):
            component_attribute = (
                bom_line.component_match_attribute_id or ptav.attribute_id
            )
            product_attribute_value = self.env["product.attribute.value"].search(
                [
                    ("attribute_id", "=", component_attribute.id),
                    ("name", "=", ptav.product_attribute_value_id.name),
                ],
                limit=1,
            )
            if not product_attribute_value:
                return False
            combination |= self.env["product.template.attribute.value"].search(
                [
                    ("product_tmpl_id", "=", component_template.id),
                    ("attribute_id", "=", component_attribute.id),
                    (
                        "product_attribute_value_id",
                        "=",
                        product_attribute_value.id,
                    ),
                ],
                limit=1,
            )

        if not combination or len(combination.attribute_id) != len(match_attributes):
            return False

        for product in component_template.product_variant_ids.filtered("active"):
            variant_values = product.product_template_variant_value_ids
            if all(value in variant_values for value in combination):
                return product
        return False
