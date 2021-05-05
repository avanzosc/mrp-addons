# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def get_taxes_values(self):
        tax_grouped = {}
        round_curr = self.currency_id.round
        for line in self.invoice_line_ids:
            if not line.account_id or line.display_type:
                continue
            price_by = line.product_id.product_tmpl_id.price_by
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.with_context(
                base_values=line._calculate_base_values(
                    price_by)).compute_all(price_unit, self.currency_id,
                                           line.quantity, line.product_id,
                                           self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(
                    tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = round_curr(val['base'])
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += round_curr(val['base'])
        return tax_grouped


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

    def _calculate_base_values(self, price_by):

        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        currency = company_id.currency_id
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the
        # tax and the total amounts. For example, in SO/PO line, we don't
        # want to round the price unit at the precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == \
            'round_globally' else True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
        if not round_tax:
            prec += 5
        price_unit = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        quantity = self.quantity
        if price_by == 'qty':
            price_field = 1
        elif price_by == 'dimension':
            price_field = self.version_dimension
        else:
            price_field = self.version_weight
        base_value = round(price_unit * quantity * price_field, prec)
        return (base_value, base_value, base_value)

    @api.depends('version_dimension', 'version_weight')
    def _compute_price(self):
        for line in self:
            price_by = line.product_id.product_tmpl_id.price_by
            currency = line.invoice_id and line.invoice_id.currency_id or None
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = False
            if line.invoice_line_tax_ids:
                taxes = line.invoice_line_tax_ids.with_context(
                    base_values=line._calculate_base_values(
                        price_by)).compute_all(
                    price, currency, line.quantity,
                    product=line.product_id,
                    partner=line.invoice_id.partner_id)
            line.price_subtotal = price_subtotal_signed = taxes[
                'total_excluded'] if taxes else line.quantity * price
            line.price_total = taxes[
                'total_included'] if taxes else line.price_subtotal
            if line.invoice_id.currency_id and line.invoice_id.currency_id != \
                    line.invoice_id.company_id.currency_id:
                currency = line.invoice_id.currency_id
                date = line.invoice_id._get_currency_rate_date()
                price_subtotal_signed = currency._convert(
                    price_subtotal_signed,
                    line.invoice_id.company_id.currency_id,
                    line.company_id or self.env.user.company_id,
                    date or fields.Date.today())
            sign = line.invoice_id.type in ['in_refund',
                                            'out_refund'] and -1 or 1
            line.price_subtotal_signed = price_subtotal_signed * sign
