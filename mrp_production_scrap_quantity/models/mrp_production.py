# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    scrap_qty = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_scrap_qty",
        readonly=True,
        store=True,
        copy=False,
    )
    real_quantity_produced = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_real_quantity_produced",
        readonly=True,
        store=True,
        copy=False,
    )

    @api.depends("scrap_ids", "scrap_ids.product_id", "scrap_ids.scrap_qty")
    def _compute_scrap_qty(self):
        for production in self:
            scraps = production.scrap_ids.filtered(
                lambda x: x.product_id == production.product_id
            )
            production.scrap_qty = sum(scraps.mapped("scrap_qty")) if scraps else 0

    @api.depends("scrap_qty", "product_qty")
    def _compute_real_quantity_produced(self):
        for production in self:
            production.real_quantity_produced = (
                production.product_qty - production.scrap_qty
                if production.product_qty > 0
                else 0
            )
