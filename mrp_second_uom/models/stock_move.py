# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    second_uom_id = fields.Many2one(
        string='Second UOM', comodel_name='uom.uom',
        related='product_id.second_uom_id', store=True)
    qty_second_uom = fields.Float(
        string='Quantity Second UOM', compute='_compute_qty_second_uom',
        store=True)

    @api.depends('product_id', 'product_id.factor', 'product_uom_qty')
    def _compute_qty_second_uom(self):
        for line in self:
            line.qty_second_uom = line.product_qty * line.product_id.factor
