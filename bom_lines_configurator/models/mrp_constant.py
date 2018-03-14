# -*- coding: utf-8 -*-
# Copyright © 2016 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models


class MrpConstant(models.Model):
    _name = 'mrp.constant'

    description = fields.Char(string='Name')
    name = fields.Char(string='Code', required=True)
    value = fields.Float(string='Value', required=True)
