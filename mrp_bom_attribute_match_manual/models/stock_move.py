# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    bom_block_product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Block",
        compute="_compute_bom_block_product_tmpl_id",
    )

    @api.depends(
        "bom_line_id.bom_id.product_tmpl_id",
        "bom_line_id.component_template_id",
        "bom_line_id.product_id.product_tmpl_id",
        "raw_material_production_id.bom_id",
    )
    def _compute_bom_block_product_tmpl_id(self):
        for move in self:
            bom_line = move.bom_line_id
            production_bom = move.raw_material_production_id.bom_id
            if not bom_line:
                move.bom_block_product_tmpl_id = False
            elif bom_line.bom_id != production_bom:
                move.bom_block_product_tmpl_id = bom_line.bom_id.product_tmpl_id
            else:
                move.bom_block_product_tmpl_id = (
                    bom_line.component_template_id
                    or bom_line.product_id.product_tmpl_id
                )
