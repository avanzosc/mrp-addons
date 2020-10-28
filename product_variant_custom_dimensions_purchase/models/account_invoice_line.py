# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    version_dimension = fields.Float(
        string="Product Dimension",
        digits=dp.get_precision('Dimension'),
        related="purchase_line_id.version_dimension"
    )
    version_weight = fields.Float(string="Product Weight",
                                  digits=dp.get_precision('Dimension'),
                                  related="purchase_line_id.version_weight")
    total_dimension = fields.Float(string="Total Dimension",
                                   digits=dp.get_precision('Dimension'),
                                   compute="_compute_total_dimension_weight")
    total_weight = fields.Float(string="Total Weight",
                                digits=dp.get_precision('Dimension'),
                                compute="_compute_total_dimension_weight")

    @api.depends("version_dimension", "version_weight")
    def _compute_total_dimension_weight(self):
        for line in self:
            line.total_dimension = line.version_dimension * line.quantity
            line.total_weight = line.version_weight * line.quantity

    @api.depends('version_dimension', 'version_weight')
    def _compute_price(self):
        super()._compute_price()
        for line in self:
            price_by = line.product_id.product_tmpl_id.price_by
            if price_by == 'qty':
                continue
            if price_by == 'dimension':
                dimension = line.version_dimension
                line.update({
                    'price_total': line['price_total'] * dimension,
                    'price_subtotal': line['price_subtotal'] * dimension,
                    'price_subtotal_signed': line['price_subtotal_signed'] *
                                             dimension,
                })
            else:
                weight = line.version_weight
                line.update({
                    'price_total': line['price_total'] * weight,
                    'price_subtotal': line['price_subtotal'] * weight,
                    'price_subtotal_signed': line['price_subtotal_signed'] *
                                             weight,
                })
