# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_id = fields.Many2one(
        compute=False, related="sale_line_id.order_id", store=True
    )
    sale_line_id = fields.Many2one(
        string="Sale line",
        comodel_name="sale.order.line",
        compute="_compute_sale_line_id",
        store=True,
        copy=False,
    )
    sale_line_product_id = fields.Many2one(
        string="Sale Line Product",
        comodel_name="product.product",
        related="sale_line_id.product_id",
        store=True,
        copy=False,
    )
    mrp_production_parent_id = fields.Many2one(
        string="Production Parent",
        comodel_name="mrp.production",
    )

    @api.depends(
        "source_procurement_group_id",
        "source_procurement_group_id.sale_id",
        "mrp_production_parent_id",
        "mrp_production_parent_id.source_procurement_group_id",
        "mrp_production_parent_id.source_procurement_group_id.sale_id",
    )
    def _compute_sale_line_id(self):
        for production in self:
            sale_line_id = self.env["sale.order.line"]
            procurement_group = production.source_procurement_group_id
            if procurement_group.sale_id:
                sale_line = procurement_group.sale_id.order_line.filtered(
                    lambda x: x.product_id == production.product_id
                    and x.product_uom_qty == production.product_qty
                )
                if sale_line:
                    sale_line_id = sale_line.id
            else:
                if (
                    production.mrp_production_parent_id
                    and production.mrp_production_parent_id.sale_line_id
                ):
                    sale_line_id = production.mrp_production_parent_id.sale_line_id.id
            production.sale_line_id = sale_line_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "origin" in vals and vals.get("origin"):
                cond = [("name", "=", vals.get("origin"))]
                production_parent = self.search(cond, limit=1)
                if production_parent:
                    vals["mrp_production_parent_id"] = production_parent.id
                    if production_parent.sale_id:
                        vals["sale_id"] = production_parent.sale_id.id
        return super().create(vals_list)
