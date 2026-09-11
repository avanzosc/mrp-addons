# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_laser_cut = fields.Boolean(
        string="Laser Cut Product",
        help="Mark finished products replenished by laser cutting so they "
        "appear in the dedicated laser cutting replenishment view and can be "
        "added to a laser cutting order.",
    )
    laser_material_id = fields.Many2one(
        comodel_name="product.product",
        string="Raw Material",
        compute="_compute_laser_material_id",
        store=True,
        help="Raw material this product is cut from, taken from the first of "
        "its Bills of Materials that has a laser operation.",
    )

    @api.depends("bom_ids.laser_material_id", "bom_ids.sequence")
    def _compute_laser_material_id(self):
        for template in self:
            laser_boms = template.bom_ids.filtered("laser_material_id")
            template.laser_material_id = laser_boms[:1].laser_material_id
