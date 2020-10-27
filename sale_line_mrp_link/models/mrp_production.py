# © 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', store=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Customer', store=True,
        related='sale_line_id.order_id.partner_id')
    sale_order_id = fields.Many2one(
        comodel_name='sale.order', string='Sale Order', store=True,
        related='sale_line_id.order_id')


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Sale lines', copy=False)
