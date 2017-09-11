# -*- coding: utf-8 -*-
# Copyright 2017 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    bom_child_ids = fields.One2many(
        comodel_name='mrp.bom', inverse_name='parent_bom',
        string='Child BoM', copy=False)

    @api.multi
    def button_new_version(self):
        return super(MrpBom, self.with_context(from_new_version=True)
                     ).button_new_version()

    @api.multi
    def button_historical(self):
        bom_historicize = self.env['mrp.config.settings']._get_parameter(
            'bom.historicize')
        if self.env.context.get('from_new_version', False) and not \
                (bom_historicize and bom_historicize.value == 'True'):
            return True
        return super(MrpBom, self).button_historical()
