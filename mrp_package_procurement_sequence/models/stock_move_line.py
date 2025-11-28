# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import re

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_create_package(self, base_prefix=None):
        production = self.move_id.production_id
        if not production:
            return super().action_create_package(base_prefix)

        procurement_group = production.procurement_group_id
        procurement_group._compute_packaged_finished_moves()
        count = production.packaged_finished_moves

        if base_prefix == self.reference:
            prefix = "".join(re.findall(r"\d", procurement_group.name))
            increment = True
        else:
            prefix = base_prefix
            increment = not (
                self.result_package_id and self.result_package_id.name == base_prefix
            )

        next_number = count + 1 if increment else count
        package_name = f"{prefix}-{next_number:02}"

        return self.env["stock.quant.package"].create({"name": package_name})
