# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class QcTestProof(models.Model):
    _name = "qc.test.proof"
    _description = "Test Proof"

    name = fields.Char(string="Name")
    type = fields.Selection(
        selection=[
            ("qualitative", "Qualitative"),
            ("quantitative", "Quantitative"),
        ],
        string="Type",
    )
