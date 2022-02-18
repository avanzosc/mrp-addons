# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    standard_price = fields.Float(
        string='Standard cost',
        related='product_id.standard_price',
        store=True)
    estimate_subcost = fields.Float(
        string='Estimate Sub Cost',
        compute='_compute_estimate_subcost')
    real_subcost = fields.Float(
        string='Real Sub Cost',
        compute='_compute_real_subcost',
        store=True)

    @api.depends("standard_price", "product_uom_qty")
    def _compute_estimate_subcost(self):
        for record in self:
            record.estimate_subcost = (
                record.product_uom_qty * record.standard_price)

    @api.depends("standard_price", "quantity_done")
    def _compute_real_subcost(self):
        for record in self:
            record.real_subcost = (
                record.quantity_done * record.standard_price)
