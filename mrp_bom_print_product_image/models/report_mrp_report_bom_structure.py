# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_bom_array_lines(
        self, data, level, unfolded_ids, unfolded, parent_unfolded=True
    ):
        values = super()._get_bom_array_lines(
            data, level, unfolded_ids, unfolded, parent_unfolded=parent_unfolded
        )
        bom = data.get("bom")
        for value in values:
            value["product_image"] = False
            if value.get("type", False) == "component":
                for line in bom.bom_line_ids:
                    if (
                        value.get("name") == line.display_name
                        and value.get("quantity") == line.product_qty
                    ):
                        if line.product_image:
                            value["product_image"] = line.product_image
                        break
        return values
