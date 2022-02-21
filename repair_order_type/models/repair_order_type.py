# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class RepairOrderType(models.Model):
    _name = 'repair.order.type'
    _description = 'Repair Order Type'

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref('repair.seq_repair')
        return [('code', '=', seq_type.code)]

    name = fields.Char(string='Name', required=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Entry Sequence',
        copy=False,
        domain=_get_domain_sequence_id)
    location_id = fields.Many2one(
        string='Location Origin',
        comodel_name='stock.location')
    location_dest_id = fields.Many2one(
        string='Destination Location',
        comodel_name='stock.location')
