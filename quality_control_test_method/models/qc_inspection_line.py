# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    test_method_id = fields.Many2one(
        string='Method', comodel_name='qc.test.method')
    test_proof_id = fields.Many2one(
        string='Proof', comodel_name='qc.test.proof')
