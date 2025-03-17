# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class BomStructureXlsx(models.AbstractModel):
    _inherit = "report.mrp_bom_structure_xlsx.bom_structure_xlsx"

    def generate_xlsx_report(self, workbook, data, objects):
        super().generate_xlsx_report(workbook, data, objects)
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
            _("Layer"),
            _("Designator"),
            _("Manufacturer code"),
            _("Cost Price"),
            _("Last Purchase Price"),
            _("Last Purchase Currency"),
            _("Last Purchase Quantity"),
            _("Manual Standard Cost"),
            _("Forecast Quantity"),
            _("Stock Real"),
        ]
        sheet = workbook.get_worksheet_by_name("BOM Structure")
        sheet.write_row(1, 0, sheet_title, title_style)
        return workbook

    def print_bom_children(self, ch, sheet, row, level):
        row = super().print_bom_children(ch, sheet, row, level)
        extra_data = [
            ch.layer if ch.layer else "",
            ch.designator if ch.designator else "",
            ch.markings if ch.markings else "",
            ch.product_id.standard_price,
            ch.product_id.last_purchase_price,
            (
                ch.product_id.last_purchase_currency_id.name
                if ch.product_id.last_purchase_currency_id
                else ""
            ),
            ch.product_id.last_purchase_line_id.product_qty,
            ch.product_id.manual_standard_cost,
            ch.product_id.virtual_available,
            ch.product_id.qty_available,
        ]
        col_start = 7
        for idx, data in enumerate(extra_data):
            sheet.write(row - 1, col_start + idx, data)
        return row
