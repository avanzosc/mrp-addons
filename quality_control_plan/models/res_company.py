# -*- coding: utf-8 -*-
# Copyright 2018 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    sample_warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Sample Warehouse')
