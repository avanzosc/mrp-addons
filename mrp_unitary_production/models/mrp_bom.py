# -*- coding: utf-8 -*-
# Copyright 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    unitary_production = fields.Boolean(string='Unitary Production')
