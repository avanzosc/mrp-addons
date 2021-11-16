# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class QcTestProof(models.Model):
    _name = 'qc.test.proof'
    _description = 'Test Proof'

    name = fields.Char(string='Name')
    type = fields.Selection(
        [("qualitative", "Qualitative"), ("quantitative", "Quantitative")],
        string="Type")
