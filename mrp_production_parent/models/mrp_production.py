# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_id = fields.Many2one(
        compute="_compute_sale_id",
        related=False,
    )
    mrp_production_parent_id = fields.Many2one(
        string="Production Parent",
        comodel_name="mrp.production",
    )

    @api.depends(
        "source_procurement_group_id",
        "source_procurement_group_id.sale_id",
        "mrp_production_parent_id.source_procurement_group_id",
        "mrp_production_parent_id.source_procurement_group_id.sale_id",
    )
    def _compute_sale_id(self):
        for production in self:
            sale_id = self.env["sale.order"]
            procurement_group = production.source_procurement_group_id
            if procurement_group.sale_id:
                sale_id = procurement_group.sale_id.id
            else:
                if production.mrp_production_parent_id:
                    procurement_group = (
                        production.mrp_production_parent_id.source_procurement_group_id
                    )
                    if procurement_group.sale_id:
                        sale_id = procurement_group.sale_id.id
            production.sale_id = sale_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "origin" in vals and vals.get("origin"):
                cond = [("name", "=", vals.get("origin"))]
                production_parent = self.search(cond, limit=1)
                if production_parent:
                    vals["mrp_production_parent_id"] = production_parent.id
        return super().create(vals_list)
