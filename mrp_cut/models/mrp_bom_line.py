# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    long_cut = fields.Float(string='Long Cut (mm)', default=0)
    qty_pieces_set = fields.Integer(
        string='Quantity of Pieces in Set', default=1)
    waste_rate = fields.Float(
        string='Waste Rate', default=1.0)
    qty_second_uom = fields.Float(
        string='Quantity in Second UOM', compute='_compute_qty_second_uom',
        store=True)
    second_uom_id = fields.Many2one(
        string='Second UOM', comodel_name='uom.uom',
        related='product_id.second_uom_id', store=True)
    pieces_second_uom = fields.Float(
        string='Pieces second UOM', compute='_compute_pieces_second_uom',
        store=True)

    @api.onchange('long_cut')
    def onchange_waste_rate(self):
        if self.long_cut:
            if self.long_cut <= 1000:
                self.waste_rate = 1.08
            if self.long_cut > 1000 and self.long_cut <= 2300:
                self.waste_rate = 1.12
            if self.long_cut > 2300 and self.long_cut <= 3000:
                self.waste_rate = 1.15
            if self.long_cut > 3000:
                self.waste_rate = 1.2

    @api.depends('product_id', 'product_id.factor', 'product_qty')
    def _compute_qty_second_uom(self):
        for line in self:
            line.qty_second_uom = line.product_qty * line.product_id.factor

    @api.depends('product_id', 'product_id.factor', 'long_cut',
                 'qty_pieces_set')
    def _compute_pieces_second_uom(self):
        for line in self:
            if line.long_cut and line.qty_pieces_set:
                line.pieces_second_uom = line.product_id.factor / (
                    line.long_cut / 1000) * line.qty_pieces_set

    @api.onchange('long_cut', 'qty_pieces_set', 'waste_rate')
    def onchange_product_qty(self):
        self.product_qty = self.long_cut / 1000 * self.qty_pieces_set * (
            self.waste_rate)

    @api.onchange('long_cut', 'product_id.product_length')
    def onchange_long_cut(self):
        if self.long_cut > 0 and self.product_id.product_length and self.long_cut / 1000 > self.product_id.product_length:
            raise ValidationError(
                _("The long cut can't be longer than the length of the product"))
