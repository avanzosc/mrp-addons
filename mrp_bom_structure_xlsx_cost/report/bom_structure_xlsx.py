import logging

from odoo import _, models
from odoo.exceptions import CacheMiss

_logger = logging.getLogger(__name__)


class BomStructureXlsxL1(models.AbstractModel):
    _name = "report.mrp_bom_structure_xlsx_cost.bom_structure_xlsx_cost"
    _description = "BOM Structure XLSX Level 1 Report"
    _inherit = "report.mrp_bom_structure_xlsx.bom_structure_xlsx"

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
        # self.env.cache.invalidate()
        try:
            for child in ch.child_line_ids:
                i = self.print_bom_children(child, sheet, i, j)

        except CacheMiss:
            # The Bom has no childs, thus it is the last level.
            # When a BoM has no childs, chlid_line_ids is None, this creates a
            # CacheMiss Error. However, this is expected because there really
            # cannot be child_line_ids.
            pass

        j -= 1
        return i

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 11.0"}
        )
        sheet = workbook.add_worksheet(_("BOM Structure"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 40)
        sheet.set_column(1, 2, 20)
        sheet.set_column(3, 3, 40)
        sheet.set_column(4, 6, 20)
        bold = workbook.add_format({"bold": True})
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )
        sheet_title = [
            _("BOM Name"),
            _("Level"),
            _("Product Reference"),
            _("Product Name"),
            _("Quantity"),
            _("Unit of Measure"),
            _("Reference"),
            _("Cost"),
        ]
        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)
        sheet.freeze_panes(2, 0)
        i = 2
        for o in objects:
            sheet.write(i, 0, o.product_tmpl_id.name or "", bold)
            sheet.write(i, 1, "", bold)
            sheet.write(i, 2, o.product_id.default_code or "", bold)
            sheet.write(i, 3, o.product_id.name or "", bold)
            sheet.write(i, 4, o.product_qty, bold)
            sheet.write(i, 5, o.product_uom_id.name or "", bold)
            sheet.write(i, 6, o.code or "", bold)
            sheet.write(i, 7, o.product_id.standard_price or "", bold)
            i += 1
            j = 0
            for ch in o.bom_line_ids:
                i = self.print_bom_children(ch, sheet, i, j)
