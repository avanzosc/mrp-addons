# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    estimated_scrap_cost = fields.Float(
        store=True,
        copy=False,
        compute="_compute_estimated_scrap_cost",
    )
    real_scrap_cost = fields.Float(
        store=True,
        copy=False,
        compute="_compute_real_scrap_cost",
    )

    @api.depends("price_unit", "product_loss_qty")
    def _compute_estimated_scrap_cost(self):
        for move in self:
            move.estimated_scrap_cost = move.price_unit * move.product_loss_qty

    @api.depends(
        "raw_material_production_id",
        "raw_material_production_id.scrap_ids",
        "raw_material_production_id.scrap_ids.state",
        "raw_material_production_id.scrap_ids.scrap_cost",
    )
    def _compute_real_scrap_cost(self):
        for move in self:
            real_scrap_cost = 0
            if (
                move.state not in ("draft", "cancel")
                and move.raw_material_production_id
                and move.raw_material_production_id.scrap_ids
            ):
                scraps = move.raw_material_production_id.scrap_ids.filtered(
                    lambda x: x.product_id == move.product_id and x.state == "done"
                )
                if scraps:
                    real_scrap_cost = sum(scraps.mapped("scrap_cost"))
            move.real_scrap_cost = real_scrap_cost
