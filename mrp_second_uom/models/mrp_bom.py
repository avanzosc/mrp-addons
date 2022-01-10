# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    second_uom_id = fields.Many2one(
        string='Second UOM', comodel_name='uom.uom',
        related='product_tmpl_id.second_uom_id', store=True)
    qty_second_uom = fields.Float(
        string='Quantity Second UOM')
    is_calculated = fields.Boolean(
        string='Is calculated', default=False, store=False)

    @api.onchange('product_qty', 'product_tmpl_id.factor', 'product_tmpl_id')
    def onchange_qty_second_uom(self):
        if self.product_qty and (
            self.product_tmpl_id.factor) and (
                self.is_calculated is False):
            self.qty_second_uom = (
                self.product_qty * self.product_tmpl_id.factor)
            self.is_calculated = True
        else:
            self.is_calculated = False

    @api.onchange('qty_second_uom', 'product_tmpl_id.factor_inverse')
    def onchange_product_qty(self):
        if self.qty_second_uom and (
            self.product_tmpl_id.factor_inverse) and (
                self.is_calculated is False):
            self.product_qty = (
                self.qty_second_uom * self.product_tmpl_id.factor_inverse)
            self.is_calculated = True
        else:
            self.is_calculated = False
