# -*- coding: utf-8 -*-
# Copyright 2014 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mrp_production_follower_ids = fields.Many2many(
        comodel_name="res.partner", string="Production followers"
    )

    @api.model_create_multi
    def create(self, values):
        productions = super(MrpProduction, self).create(values)
        cond = [('mrp_production_follower', '=', True)]
        users = self.env['res.users'].search(cond)
        if users:
            for production in productions:
                production.mrp_production_follower_ids = [
                    (6, 0, users.mapped('partner_id').ids)
                ]
        return productions
