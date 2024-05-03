# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    stencil_product_ids = fields.Many2many(
        string="Stencil products",
        comodel_name="mrp.bom.stencil.product",
        compute="_compute_stencil_product_ids",
        store=True,
        readonly=True,
        copy=False,
    )

    @api.depends(
        "production_id",
        "production_id.move_raw_ids",
        "production_id.move_raw_ids.workorder_id",
        "production_id.move_raw_ids.bom_line_id",
    )
    def _compute_stencil_product_ids(self):
        for workorder in self:
            stencil_product_ids = []
            if workorder.production_id and workorder.production_id.move_raw_ids:
                moves = workorder.production_id.move_raw_ids.filtered(
                    lambda x: x.workorder_id.id == workorder.id
                )
                boms = moves.bom_line_id.mapped("bom_id")
                for bom in boms:
                    for stencil_product in bom.stencil_product_ids:
                        stencil_product_ids.append(stencil_product.id)
            workorder.stencil_product_ids = [(6, 0, stencil_product_ids)]
