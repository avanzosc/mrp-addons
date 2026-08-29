# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class QcInspectionSetTest(models.TransientModel):
    _inherit = "qc.inspection.set.test"

    def action_create_test(self):
        result = super().action_create_test()
        inspection = self.env["qc.inspection"].browse(self.env.context["active_id"])
        inspection.automatic_claims = self.test.automatic_claims
        inspection.automatic_claims_by_line = self.test.automatic_claims_by_line
        return result
