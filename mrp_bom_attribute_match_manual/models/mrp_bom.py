# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    match_on_attribute_ids = fields.Many2many(readonly=False)
    component_match_attribute_ids = fields.Many2many(
        comodel_name="product.attribute",
        relation="mrp_bom_line_component_match_attribute_rel",
        column1="bom_line_id",
        column2="attribute_id",
        string="Component Match Attributes",
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

    def onchange_bom_structure(self):
        if self.type == "phantom":
            return
        return super().onchange_bom_structure()

    def _get_mapped_component_template_product(self, bom_line, bom_product_id):
        component_template = bom_line.component_template_id
        parent_values = bom_product_id.product_template_attribute_value_ids.filtered(
            lambda value: value.attribute_id in bom_line.match_on_attribute_ids
        )
        if not parent_values:
            return False
        component_values = self.env["product.template.attribute.value"]
        for parent_value in parent_values:
            component_values |= self.env["product.template.attribute.value"].search(
                [
                    ("product_tmpl_id", "=", component_template.id),
                    ("attribute_id", "in", bom_line.component_match_attribute_ids.ids),
                    (
                        "product_attribute_value_id.name",
                        "=",
                        parent_value.product_attribute_value_id.name,
                    ),
                ],
                limit=1,
            )
        if len(component_values) != len(parent_values):
            return False
        product = component_template._get_variant_for_combination(component_values)
        return product if product and product.active else False

    def _get_component_template_product(
        self, bom_line, bom_product_id, line_product_id
    ):
        if not bom_line.component_template_id:
            return line_product_id

        if bom_line.component_match_attribute_ids:
            return self._get_mapped_component_template_product(bom_line, bom_product_id)
        return super()._get_component_template_product(
            bom_line, bom_product_id, line_product_id
        )
