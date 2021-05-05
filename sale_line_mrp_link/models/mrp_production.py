# Copyright 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', store=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Customer', store=True,
        compute="_compute_partner_id_commitment_date")
    commitment_date = fields.Datetime(
        compute="_compute_partner_id_commitment_date",
        string='Commitment Date', store=True)

    @api.onchange
    def _onchange_sale_line_id(self):
        self.ensure_one()
        if self.sale_line_id:
            self.sale_order_id = self.sale_line_id.order_id

    @api.depends("sale_order_id", "sale_line_id")
    def _compute_partner_id_commitment_date(self):
        for production in self:
            production.partner_id = (
                production.sale_order_id.partner_id or
                production.sale_line_id.order_id.partner_id)
            production.commitment_date = (
                production.sale_order_id.commitment_date or
                production.sale_line_id.order_id.commitment_date)


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Sale Line', copy=False)
