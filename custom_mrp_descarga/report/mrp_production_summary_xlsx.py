# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class ReportMrpProductionsummaryXlsx(models.AbstractModel):
    _name = "report.mrp_production_summary_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "MRP Production Summary Report"

    def generate_xlsx_report(self, workbook, data, objects):
        table_header = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "#D7E4BC",
            }
        )
        summary = workbook.add_format(
            {
                "bold": True,
                "num_format": "#,##0.00;(#,##0.00)",
            }
        )
        int_format = workbook.add_format(
            {
                "num_format": "#,##0;(#,##0)",
            }
        )
        two_decimal_format = workbook.add_format(
            {
                "num_format": "#,##0.00;(#,##0.00)",
            }
        )
        three_decimal_format = workbook.add_format(
            {
                "num_format": "#,##0.000;(#,##0.000)",
            }
        )
        eight_decimal_format = workbook.add_format(
            {
                "num_format": "#,##0.00000000;(#,##0.00000000)",
            }
        )
        result_int_format = workbook.add_format(
            {
                "bold": True,
                "fg_color": "#afd095",
                "num_format": "#,##0;(#,##0)",
            }
        )
        result_two_decimal = workbook.add_format(
            {
                "bold": True,
                "fg_color": "#afd095",
                "num_format": "#,##0.00;(#,##0.00)",
            }
        )
        result_three_decimal = workbook.add_format(
            {
                "bold": True,
                "fg_color": "#afd095",
                "num_format": "#,##0.000;(#,##0.000)",
            }
        )
        result_summary = workbook.add_format(
            {
                "bold": True,
                "fg_color": "#afd095",
                "num_format": "#,##0.000;(#,##0.000)",
            }
        )
        table_header.set_text_wrap()
        summary.set_text_wrap()
        int_format.set_text_wrap()
        two_decimal_format.set_text_wrap()
        three_decimal_format.set_text_wrap()
        eight_decimal_format.set_text_wrap()
        result_three_decimal.set_text_wrap()
        result_two_decimal.set_text_wrap()
        result_summary.set_text_wrap()
        table_detail_right_num = workbook.add_format(
            {
                "border": 1,
                "align": "right",
                "valign": "vcenter",
            }
        )
        table_detail_right_num.set_num_format("#,##0.00")
        worksheet = workbook.add_worksheet("Resumen de matanza")
        worksheet.write(0, 0, _("Resumen de matanza"), table_header)
        for i in range(0, 10):
            worksheet.set_column(0, i, 20)
        n = 1
        m = 0
        worksheet.write(n, m, _("%"), table_header)
        m += 1
        worksheet.write(n, m, _("Código"), table_header)
        m += 1
        worksheet.write(n, m, _("Definición"), table_header)
        m += 1
        worksheet.write(n, m, _("Envases"), table_header)
        m += 1
        worksheet.write(n, m, _("Unidades"), table_header)
        m += 1
        worksheet.write(n, m, _("KGs"), table_header)
        m += 1
        worksheet.write(n, m, _("Peso medio"), table_header)
        m += 1
        worksheet.write(n, m, _("Coste"), table_header)
        m += 1
        worksheet.write(n, m, _("Importe"), table_header)
        m += 1
        worksheet.write(n, m, _("% vivo"), table_header)
        for m in range(m + 1, 10):
            worksheet.write(n, m, "", table_header)
        movelines = objects.mapped("move_line_ids")
        categories = []
        products = []
        origin_qty = sum(objects.mapped("origin_qty"))
        sum_live_percentage = 0
        for line in movelines:
            if line.product_category_id not in categories:
                categories.append(line.product_category_id)
                categ_lines = movelines.filtered(
                    lambda c: c.product_category_id == line.product_category_id
                )
                categ_container = sum(categ_lines.mapped("container"))
                categ_unit = sum(categ_lines.mapped("unit"))
                categ_qty_done = sum(categ_lines.mapped("qty_done"))
                categ_average_weight = (
                    (categ_qty_done / categ_unit) if categ_unit else 0
                )
                categ_amount = sum(categ_lines.mapped("amount"))
                categt_applied_price = round(
                    (categ_amount / categ_qty_done) if categ_qty_done != 0 else 0, 3
                )
                for product in categ_lines:
                    if product.product_id not in products:
                        n += 1
                        m = 0
                        products.append(product.product_id)
                        product_lines = categ_lines.filtered(
                            lambda c: c.product_id == product.product_id
                        )
                        product_container = sum(product_lines.mapped("container"))
                        product_unit = sum(product_lines.mapped("unit"))
                        product_qty_done = sum(product_lines.mapped("qty_done"))
                        product_percentage = (
                            (product_qty_done * 100 / categ_qty_done)
                            if categ_qty_done
                            else 0
                        )
                        product_average_weight = (
                            (product_qty_done / product_unit) if product_unit else 0
                        )
                        product_amount = sum(product_lines.mapped("amount"))
                        product_applied_price = (
                            (product_amount / product_qty_done)
                            if product_qty_done
                            else 0
                        )
                        worksheet.write(
                            n, m, round(product_percentage, 2), two_decimal_format
                        )
                        m += 1
                        worksheet.write(n, m, product.product_id.default_code)
                        m += 1
                        worksheet.write(n, m, product.product_id.name)
                        m += 1
                        worksheet.write(n, m, product_container)
                        m += 1
                        worksheet.write(n, m, product_unit)
                        m += 1
                        worksheet.write(n, m, product_qty_done)
                        m += 1
                        worksheet.write(
                            n, m, product_average_weight, three_decimal_format
                        )
                        m += 1
                        worksheet.write(
                            n, m, product_applied_price, three_decimal_format
                        )
                        m += 1
                        worksheet.write(
                            n, m, round(product_amount, 2), two_decimal_format
                        )
                        m += 1
                        worksheet.write(
                            n,
                            m,
                            round(product_qty_done / origin_qty * 100, 2),
                            two_decimal_format,
                        )
                n += 1
                m = 0
                worksheet.write(n, m, 100, result_int_format)
                m += 1
                worksheet.write(n, m, "", result_int_format)
                m += 1
                worksheet.write(n, m, line.product_category_id.name, result_int_format)
                m += 1
                worksheet.write(n, m, categ_container, result_int_format)
                m += 1
                worksheet.write(n, m, categ_unit, result_int_format)
                m += 1
                worksheet.write(n, m, categ_qty_done, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_average_weight, result_three_decimal)
                m += 1
                worksheet.write(n, m, categt_applied_price, result_three_decimal)
                m += 1
                worksheet.write(n, m, categ_amount, result_two_decimal)
                m += 1
                worksheet.write(
                    n, m, categ_qty_done / origin_qty * 100, result_two_decimal
                )
                sum_live_percentage += categ_qty_done / origin_qty * 100
        different_date_planned = objects.mapped("saca_date")
        different_date_planned = list({d for d in different_date_planned})
        n += 1
        m = 0
        worksheet.write(n, m, "Partes de matanza", result_int_format)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        m += 1
        total_containers = sum(movelines.mapped("container"))
        worksheet.write(n, m, total_containers, result_int_format)
        m += 1
        total_unit = sum(movelines.mapped("unit"))
        worksheet.write(n, m, total_unit, result_int_format)
        m += 1
        total_qty_done = sum(movelines.mapped("qty_done"))
        worksheet.write(n, m, total_qty_done, result_two_decimal)
        m += 1
        worksheet.write(n, m, total_qty_done / total_unit, result_three_decimal)
        m += 1
        total_amount = sum(movelines.mapped("amount"))
        total_average_price = total_amount / total_qty_done
        worksheet.write(n, m, total_average_price, result_three_decimal)
        m += 1
        worksheet.write(n, m, total_amount, result_two_decimal)
        m += 1
        worksheet.write(n, m, total_qty_done / origin_qty * 100, result_two_decimal)
        n += 1
        m = 0
        worksheet.write(n, m, "Datos de granja", result_int_format)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        m += 1
        download_unit = sum(objects.mapped("download_unit"))
        worksheet.write(n, m, download_unit, result_int_format)
        m += 1
        worksheet.write(n, m, origin_qty, result_two_decimal)
        m += 1
        real_average_weight = sum(objects.mapped("real_average_weight")) / len(objects)
        worksheet.write(n, m, real_average_weight, result_three_decimal)
        m += 1
        purchase_price = sum(objects.mapped("purchase_price"))
        price_unit = purchase_price / origin_qty
        worksheet.write(n, m, price_unit, result_three_decimal)
        m += 1
        worksheet.write(n, m, purchase_price, result_two_decimal)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        n += 1
        m = 0
        days = len(different_date_planned)
        worksheet.write(n, m, "Días", result_int_format)
        m += 1
        worksheet.write(n, m, days, result_int_format)
        m += 8
        worksheet.write(n, m, sum_live_percentage, result_two_decimal)
        n += 1
        m = 0
        worksheet.write(n, m, "Fichas", result_int_format)
        m += 1
        productions = len(objects)
        worksheet.write(n, m, productions, result_int_format)
        n += 1
        m = 0
        worksheet.write(n, m, "Total Kms", result_int_format)
        kms = objects.saca_line_id.mapped("distance_done")
        m += 1
        total_kms = sum(kms)
        worksheet.write(n, m, total_kms, result_int_format)
        n += 1
        m = 0
        worksheet.write(n, m, "Media personal", result_int_format)
        personal = objects.saca_line_id.mapped("staff")
        average_personal = sum(personal) / productions
        m += 1
        worksheet.write(n, m, average_personal, result_int_format)
        n += 1
        m = 0
        worksheet.write(n, m, "Media diaria", result_int_format)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        m += 1
        worksheet.write(n, m, "", result_int_format)
        m += 1
        worksheet.write(n, m, total_unit / days, result_two_decimal)
        m += 1
        worksheet.write(n, m, total_qty_done / days, result_two_decimal)
        m += 1
        worksheet.write(n, m, total_qty_done / total_unit / days, result_three_decimal)
        m += 1
        worksheet.write(n, m, total_average_price / days, result_three_decimal)
        m += 1
        worksheet.write(n, m, total_amount / days, result_two_decimal)
        m += 1
        worksheet.write(n, m, "", result_int_format)
