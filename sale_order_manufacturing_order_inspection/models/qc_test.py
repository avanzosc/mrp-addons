# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class QcTest(models.Model):
    _inherit = "qc.test"

    qc_test_label_ids = fields.Many2many(
        string="Test Labels", comodel_name="qc.test.label"
    )
