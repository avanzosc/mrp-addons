# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_laser_cut = fields.Boolean(
        help="Check this on finished products replenished by laser "
        "cutting, so they show up in the dedicated laser cut "
        "replenishment view.",
    )
    laser_material_id = fields.Many2one(
        comodel_name="product.product",
        compute="_compute_laser_material_id",
        store=True,
        help="Raw sheet material this product is cut from, according to "
        "its Bill of Materials.",
    )

    @api.depends("bom_ids.laser_material_id")
    def _compute_laser_material_id(self):
        for template in self:
            bom = template.bom_ids[:1]
            template.laser_material_id = bom.laser_material_id
