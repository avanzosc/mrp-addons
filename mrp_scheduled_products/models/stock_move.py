# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    production_product_line_id = fields.Many2one(
        comodel_name='mrp.production.product.line', string='Scheduled Product')
