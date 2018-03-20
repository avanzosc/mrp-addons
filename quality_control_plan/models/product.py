# -*- coding: utf-8 -*-
# Copyright 2018 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from dateutil.relativedelta import relativedelta

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'years': lambda interval: relativedelta(years=interval)
}


class ProductQualityControlPlanCron(models.Model):

    _name = 'product.quality.control.plan.cron'

    @api.multi
    def _get_default_next_date(self):
        date = fields.Date.from_string(fields.Date.context_today(self))
        return date.replace(month=1, day=1)

    qc_test_id = fields.Many2one(comodel_name='qc.test', string='QC Test')
    interval_number = fields.Integer(string='Number')
    interval_type = fields.Selection(
        selection=[('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'),
                   ('years', 'Years')], string='Interval', default='months')
    next_date = fields.Date(string='Next Date', default=_get_default_next_date)
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product')

    @api.multi
    def update_next_date(self):
        for record in self:
            record.next_date = (fields.Date.from_string(record.next_date) +
                                _intervalTypes[record.interval_type
                                               ](record.interval_number))


class ProductProduct(models.Model):

    _inherit = 'product.product'

    subject_to_qcp = fields.Boolean(string='Subject to Quality Control Plan')
    sample_qty = fields.Float(string='Sample Quantity')
    plan_control_cron_ids = fields.One2many(
        comodel_name='product.quality.control.plan.cron',
        inverse_name='product_id', string='Plan Control Cron Lines')
