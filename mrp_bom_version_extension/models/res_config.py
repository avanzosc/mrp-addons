# -*- coding: utf-8 -*-
# Copyright 2017 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class MrpConfigSettings(models.TransientModel):

    _inherit = 'mrp.config.settings'

    bom_historicize = fields.Boolean(
        string="Historicize BoM",
        help="Desactivate this field if you don't want to historicize the bom "
        "when a new version is created.")

    def _get_parameter(self, key, default=False):
        param_obj = self.env['ir.config_parameter']
        rec = param_obj.search([('key', '=', key)])
        return rec or default

    def _write_or_create_param(self, key, value):
        param_obj = self.env['ir.config_parameter']
        rec = self._get_parameter(key)
        if rec:
            rec.value = str(value)
        else:
            param_obj.create({'key': key, 'value': str(value)})

    @api.multi
    def get_default_parameter_bom_historicize(self):
        def get_value(key, default=''):
            rec = self._get_parameter(key)
            return rec and rec.value and rec.value != 'False' or default
        return {'bom_historicize': get_value('bom.historicize', False)}

    @api.multi
    def set_parameter_bom_historicize(self):
        self._write_or_create_param('bom.historicize', self.bom_historicize)
