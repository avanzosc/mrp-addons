# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        n = 1
        while True:
            name = "{}-{:02d}".format(self.name, n)
            existe = self.search_count([("name", "=", name)])
            if not existe:
                break
            n += 1
        default["name"] = name
        default["state"] = "draft"
        new_inspection = super().copy(default=default)
        if new_inspection.test:
            new_inspection.inspection_lines.unlink()
            new_inspection.write(
                {
                    "inspection_lines": (
                        new_inspection._prepare_inspection_lines(new_inspection.test)
                    ),
                }
            )
        return new_inspection
