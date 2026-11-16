# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    laser_material_id = fields.Many2one(
        comodel_name="product.product",
        string="Raw Material",
        compute="_compute_laser_material_id",
        store=True,
        help="Component of this Bill of Materials whose operation runs on a "
        "laser work center, i.e. the raw material this product is cut from.",
    )

    @api.depends(
        "bom_line_ids.operation_id.workcenter_id.is_laser",
        "bom_line_ids.product_id",
    )
    def _compute_laser_material_id(self):
        for bom in self:
            laser_line = bom.bom_line_ids.filtered(
                lambda line: line.operation_id.workcenter_id.is_laser
            )[:1]
            bom.laser_material_id = laser_line.product_id
