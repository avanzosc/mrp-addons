# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _prepare_inspection_lines(self, test, force_fill=False):
        result = super(QcInspection, self)._prepare_inspection_lines(
            test, force_fill=False
        )
        for line in result:
            test_line = line[2]["test_line"]
            line[2].update(
                {
                    "test_method_id": self.env["qc.test.question"]
                    .search([("id", "=", test_line)], limit=1)
                    .test_method_id.id,
                    "test_proof_id": self.env["qc.test.question"]
                    .search([("id", "=", test_line)], limit=1)
                    .test_proof_id.id,
                }
            )
        return result
