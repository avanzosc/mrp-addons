# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class QcTestQuestion(models.Model):
    _inherit = 'qc.test.question'

    test_method_id = fields.Many2one(
        string='Method', comodel_name='qc.test.method')
    test_proof_id = fields.Many2one(
        string='Proof', comodel_name='qc.test.proof')

    @api.onchange("test_proof_id")
    def onchange_type(self):
        if self.test_proof_id:
            self.type = self.test_proof_id.type

    @api.onchange('type')
    def onchange_test_proof_id(self):
        self.ensure_one()
        domain = []
        if self.type:
            domain = ['|', ('type', '=', self.type), ('type', '=', False)]
        return {'domain': {'test_proof_id': domain}}
