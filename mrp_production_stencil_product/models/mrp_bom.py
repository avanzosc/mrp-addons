# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    stencil_product_ids = fields.One2many(
        string="Stencil products",
        comodel_name="mrp.bom.stencil.product",
        inverse_name="bom_id",
        copy=True,
    )

    def copy(self, default=None):
        default = default or {}
        default_stencil_products = [
            (
                0,
                0,
                {
                    "product_id": (
                        stencil.product_id.id if stencil.product_id else False
                    ),
                    "location_id": (
                        stencil.location_id.id if stencil.location_id else False
                    ),
                    "product_uom_id": (
                        stencil.product_uom_id.id if stencil.product_uom_id else False
                    ),
                    "product_uom_qty": (
                        stencil.product_uom_qty if stencil.product_uom_qty else 0
                    ),
                },
            )
            for stencil in self.stencil_product_ids
        ]
        default["stencil_product_ids"] = default_stencil_products
        new_record = super().copy(default)
        return new_record
