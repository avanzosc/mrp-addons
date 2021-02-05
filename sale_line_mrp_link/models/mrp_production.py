# Copyright 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', store=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Customer', store=True,
        compute="_compute_partner_id")

    @api.onchange
    def _onchange_sale_line_id(self):
        self.ensure_one()
        if self.sale_line_id:
            self.sale_order_id = self.sale_line_id.order_id

    @api.depends("sale_order_id", "sale_line_id")
    def _compute_partner_id(self):
        for production in self:
            production.partner_id = (
                production.sale_order_id.partner_id or
                production.sale_line_id.order_id.partner_id)


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Sale Line', copy=False)
