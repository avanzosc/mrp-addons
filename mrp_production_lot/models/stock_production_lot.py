# -*- coding: utf-8 -*-
# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api
from dateutil.relativedelta import relativedelta


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    production_id = fields.Many2one(
        comodel_name='mrp.production', string='Production order')

    @api.onchange('production_id')
    def onchange_production_id(self):
        for lot in self:
            vals = {'mrp_date': False,
                    'life_date': False,
                    'use_date': False,
                    'removal_date': False,
                    'alert_date': False}
            lot.write(vals)
            if lot.production_id:
                date_planned = fields.Datetime.from_string(
                    lot.production_id.date_planned).date()
                lot.mrp_date = date_planned

    @api.onchange('mrp_date')
    @api.multi
    def onchange_mrp_date(self):
        for lot in self:
            if not lot.mrp_date:
                lot.life_date = False
                lot.use_date = False
                lot.removal_date = False
                lot.alert_date = False
            if lot.mrp_date:
                mrp_date = fields.Date.from_string(lot.mrp_date)
            if lot.mrp_date and lot.product_id and lot.product_id.life_time:
                lot.life_date = fields.Date.to_string(
                    mrp_date + relativedelta(days=lot.product_id.life_time))
            if lot.mrp_date and lot.product_id and lot.product_id.use_time:
                lot.use_date = fields.Date.to_string(
                    mrp_date + relativedelta(days=lot.product_id.use_time))
            if lot.mrp_date and lot.product_id and lot.product_id.removal_time:
                lot.removal_date = fields.Date.to_string(
                    mrp_date + relativedelta(days=lot.product_id.removal_time))
            if lot.mrp_date and lot.product_id and lot.product_id.alert_time:
                lot.alert_date = fields.Date.to_string(
                    mrp_date + relativedelta(days=lot.product_id.alert_time))
