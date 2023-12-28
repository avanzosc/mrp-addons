# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    parent_product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Parent Product Template",
        related="bom_id.product_tmpl_id")
    possible_bom_product_template_attribute_value_ids = fields.Many2many(
        string='Possible BOM Product Attribute Value',
        relation='rel_routing_variant',
        column1='routing_workcenter_id',
        column2='product_template_attribute_id',
        comodel_name='product.template.attribute.value',
        compute='_compute_possible_bom_product_template_attribute_value_ids',
        store=True)
    bom_product_template_attribute_value_ids = fields.Many2many(
        comodel_name="product.template.attribute.value",
        string="Apply on Variants",
        ondelete="restrict",
        domain="[('id', 'in', possible_bom_product_template_attribute_value_ids)]",
        help="BOM Product Variants needed to apply this line.")

    @api.depends(
        "parent_product_tmpl_id",
        "parent_product_tmpl_id.valid_product_template_attribute_line_ids")
    def _compute_possible_bom_product_template_attribute_value_ids(self):
        for line in self:
            line.possible_bom_product_template_attribute_value_ids = line.parent_product_tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes().product_template_value_ids._only_active()
