import logging

from odoo import models

_logger = logging.getLogger(__name__)


class BomStructureXlsxL1(models.AbstractModel):
    _name = "report.mrp_bom_structure_xlsx_cost.bom_structure_xlsx_l1_cost"
    _description = "BOM Structure XLSX Level 1 Report"
    _inherit = "report.mrp_bom_structure_xlsx_cost.bom_structure_xlsx_cost"

    def print_bom_children(self, ch, sheet, row, level):
        i, j = row, level
        j += 1
        sheet.write(i, 1, "> " * j)
        sheet.write(i, 2, ch.product_id.default_code or "")
        sheet.write(i, 3, ch.product_id.display_name or "")
        sheet.write(
            i,
            4,
            ch.product_uom_id._compute_quantity(ch.product_qty, ch.product_id.uom_id)
            or "",
        )
        sheet.write(i, 5, ch.product_id.uom_id.name or "")
        sheet.write(i, 6, ch.bom_id.code or "")
        sheet.write(
            i,
            7,
            "{:.4f}".format(
                ch.product_uom_id._compute_quantity(
                    ch.product_qty, ch.product_id.uom_id
                )
                * ch.product_id.standard_price
                or 0
            ).replace(".", ","),
        )

        i += 1
        return i
