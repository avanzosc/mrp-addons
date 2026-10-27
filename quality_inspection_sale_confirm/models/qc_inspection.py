# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _make_inspection(self, object_ref, trigger_line):
        # The OCA stock module invokes this method again at picking done.
        # Reuse the early inspection instead of creating a duplicate.
        # Only stock moves are handled; other inspection targets are untouched.
        if object_ref and object_ref._name == "stock.move":
            reference = "stock.move,%s" % object_ref.id
            existing = self.sudo().search(
                [
                    ("object_id", "=", reference),
                    ("test", "=", trigger_line.test.id),
                    ("auto_generated", "=", True),
                ],
                limit=1,
            )
            if existing:
                return existing
        return super()._make_inspection(object_ref, trigger_line)
