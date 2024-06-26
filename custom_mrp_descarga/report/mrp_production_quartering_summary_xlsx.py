# Copyright 2024 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class ReportMrpProductionQuarteringSummaryXlsx(models.AbstractModel):
    _name = "report.mrp_production_quartering_summary_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "MRP Production Quartering Summary Report"

    def generate_xlsx_report(self, workbook, data, objects):
        table_header = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D7E4BC',
        })
        summary = workbook.add_format({
            'bold': True,
            'num_format': '#,##0.00;(#,##0.00)',
        })
        int_format = workbook.add_format({
            'num_format': '#,##0;(#,##0)',
        })
        two_decimal_format = workbook.add_format({
            'num_format': '#,##0.00;(#,##0.00)',
        })
        three_decimal_format = workbook.add_format({
            'num_format': '#,##0.000;(#,##0.000)',
        })
        eight_decimal_format = workbook.add_format({
            'num_format': '#,##0.00000000;(#,##0.00000000)',
        })
        result_int_format = workbook.add_format({
            'bold': True,
            'fg_color': '#afd095',
            'num_format': '#,##0;(#,##0)',
        })
        result_two_decimal = workbook.add_format({
            'bold': True,
            'fg_color': '#afd095',
            'num_format': '#,##0.00;(#,##0.00)',
        })
        result_three_decimal = workbook.add_format({
            'bold': True,
            'fg_color': '#afd095',
            'num_format': '#,##0.000;(#,##0.000)',
        })
        result_summary = workbook.add_format({
            'bold': True,
            'fg_color': '#afd095',
            'num_format': '#,##0.000;(#,##0.000)',
        })
        table_header.set_text_wrap()
        summary.set_text_wrap()
        int_format.set_text_wrap()
        two_decimal_format.set_text_wrap()
        three_decimal_format.set_text_wrap()
        eight_decimal_format.set_text_wrap()
        result_three_decimal.set_text_wrap()
        result_two_decimal.set_text_wrap()
        result_summary.set_text_wrap()
        table_detail_right_num = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })
        table_detail_right_num.set_num_format('#,##0.00')
        worksheet = workbook.add_worksheet("Resumen de despiece")
        worksheet.write(0, 0, _("Resumen de despiece"), result_int_format)
        for i in range(0, 13):
            worksheet.set_column(0, i, 15)
        n = 2
        m = 0
        worksheet.write(n, m, _("Entradas"), table_header)
        n += 1
        worksheet.write(n, m, _("Código"), table_header)
        m += 1
        worksheet.write(n, m, _("Producto"), table_header)
        m += 1
        worksheet.write(n, m, _("Palets"), table_header)
        m += 1
        worksheet.write(n, m, _("Envases"), table_header)
        m += 1
        worksheet.write(n, m, _("Unidades"), table_header)
        m += 1
        worksheet.write(n, m, _("KG bruto"), table_header)
        m += 1
        worksheet.write(n, m, _("KG palets"), table_header)
        m += 1
        worksheet.write(n, m, _("KG envases"), table_header)
        m += 1
        worksheet.write(n, m, _("KG neto"), table_header)
        m += 1
        worksheet.write(n, m, _("Coste"), table_header)
        m += 1
        worksheet.write(n, m, _("Importe"), table_header)
        m += 1
        worksheet.write(n, m, _("Peso medio"), table_header)
        m += 1
        worksheet.write(n, m, _("% rendimiento"), table_header)
        for m in range(m + 1, 13):
            worksheet.write(n, m, "", table_header)
        entry_movelines = objects.mapped("move_line_ids")
        categories = []
        products = []
        for line in entry_movelines:
            if line.product_category_id not in categories:
                categories.append(line.product_category_id)
                categ_lines = entry_movelines.filtered(
                    lambda c: c.product_category_id == line.product_category_id
                )
                categ_pallet = sum(categ_lines.mapped("pallet"))
                categ_container = sum(categ_lines.mapped("container"))
                categ_unit = sum(categ_lines.mapped("unit"))
                categ_brut = sum(categ_lines.mapped("brut"))
                categ_pallet_weight = 0
                categ_container_weight = 0
                for line in categ_lines:
                    if line.move_id and (
                        line.move_id.raw_material_production_id
                    ) and line.move_id.raw_material_production_id.pallet_id:
                        categ_pallet_weight += line.move_id.raw_material_production_id.pallet_id.weight * line.pallet
                    if line.move_id and (
                        line.move_id.raw_material_production_id
                    ) and line.move_id.raw_material_production_id.packaging_id:
                        categ_container_weight += line.move_id.raw_material_production_id.packaging_id.weight * line.container
                categ_qty_done = sum(categ_lines.mapped("qty_done"))
                categ_average_weight = categ_qty_done / sum(
                    categ_lines.mapped("download_unit")
                ) if sum(categ_lines.mapped("download_unit")) else 0
                categ_amount = sum(categ_lines.mapped("amount"))
                categt_applied_price = round((
                    categ_amount / categ_qty_done
                ) if categ_qty_done != 0 else 0, 3)
                for product in categ_lines:
                    if product.product_id not in products:
                        n += 1
                        m = 0
                        products.append(product.product_id)
                        product_lines = categ_lines.filtered(
                            lambda c: c.product_id == product.product_id
                        )
                        product_pallet = sum(product_lines.mapped("pallet"))
                        product_container = sum(
                            product_lines.mapped("container")
                        )
                        product_unit = sum(product_lines.mapped("unit"))
                        product_brut = sum(product_lines.mapped("brut"))
                        product_pallet_weight = 0
                        product_container_weight = 0
                        for line in product_lines:
                            if line.move_id and line.move_id.raw_material_production_id and line.move_id.raw_material_production_id.pallet_id:
                                product_pallet_weight += line.move_id.raw_material_production_id.pallet_id.weight * line.pallet
                            if line.move_id and line.move_id.raw_material_production_id and line.move_id.raw_material_production_id.packaging_id:
                                product_container_weight += line.move_id.raw_material_production_id.packaging_id.weight * line.container
                        product_qty_done = sum(
                            product_lines.mapped("qty_done")
                        )
                        product_average_weight = product_qty_done / sum(
                            product_lines.mapped("download_unit")
                        ) if sum(product_lines.mapped("download_unit")) else 0
                        product_amount = sum(product_lines.mapped("amount"))
                        product_applied_price = (
                            (
                                product_amount / product_qty_done
                            ) if product_qty_done else 0
                        )
                        worksheet.write(n, m, product.product_id.default_code)
                        m += 1
                        worksheet.write(n, m, product.product_id.name)
                        m += 1
                        worksheet.write(n, m, product_pallet, int_format)
                        m += 1
                        worksheet.write(n, m, product_container, int_format)
                        m += 1
                        worksheet.write(n, m, product_unit, int_format)
                        m += 1
                        worksheet.write(n, m, product_brut, two_decimal_format)
                        m += 1
                        worksheet.write(n, m, product_pallet_weight, two_decimal_format)
                        m += 1
                        worksheet.write(n, m, product_container_weight, two_decimal_format)
                        m += 1
                        worksheet.write(n, m, product_qty_done, two_decimal_format)
                        m += 1
                        worksheet.write(
                            n, m, product_applied_price, three_decimal_format
                        )
                        m += 1
                        worksheet.write(
                            n, m, round(product_amount, 2), two_decimal_format
                        )
                        m += 1
                        worksheet.write(n, m, product_average_weight, two_decimal_format)
                        m += 1
                        worksheet.write(n, m, product_qty_done * 100 / sum(entry_movelines.mapped("qty_done")), two_decimal_format)
                n += 1
                m = 0
                worksheet.write(
                    n, m, line.product_category_id.display_name, result_int_format
                )
                m += 1
                worksheet.write(
                    n, m, "", result_int_format
                )
                m += 1
                worksheet.write(n, m, categ_pallet, result_int_format)
                m += 1
                worksheet.write(n, m, categ_container, result_int_format)
                m += 1
                worksheet.write(n, m, categ_unit, result_int_format)
                m += 1
                worksheet.write(n, m, categ_brut, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_pallet_weight, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_container_weight, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_qty_done, result_two_decimal)
                m += 1
                worksheet.write(
                    n, m, categt_applied_price, result_three_decimal
                )
                m += 1
                worksheet.write(n, m, categ_amount, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_average_weight, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_qty_done * 100 / sum(entry_movelines.mapped("qty_done")), result_two_decimal)
        n += 3
        m = 0
        worksheet.write(n, m, _("Salidas"), table_header)
        categories = []
        products = []
        out_movelines = objects.mapped("finished_move_line_ids")
        for line in out_movelines:
            if line.product_category_id not in categories:
                categories.append(line.product_category_id)
                categ_lines = out_movelines.filtered(
                    lambda c: c.product_category_id == line.product_category_id
                )
                categ_pallet = sum(categ_lines.mapped("pallet"))
                categ_container = sum(categ_lines.mapped("container"))
                categ_brut = sum(categ_lines.mapped("brut"))
                categ_pallet_weight = 0
                categ_container_weight = 0
                for line in categ_lines:
                    if line.move_id and line.move_id.production_id and line.move_id.production_id.pallet_id:
                        categ_pallet_weight += line.move_id.production_id.pallet_id.weight * line.pallet
                    if line.move_id and line.move_id.production_id and line.move_id.production_id.packaging_id:
                        categ_container_weight += line.move_id.production_id.packaging_id.weight * line.container
                categ_qty_done = sum(categ_lines.mapped("qty_done"))
                categ_amount = sum(categ_lines.mapped("amount"))
                categt_applied_price = round((categ_amount / categ_qty_done) if categ_qty_done != 0 else 0, 3)
                for product in categ_lines:
                    if product.product_id not in products:
                        n += 1
                        m = 0
                        products.append(product.product_id)
                        product_lines = categ_lines.filtered(
                            lambda c: c.product_id == product.product_id
                        )
                        product_pallet = sum(product_lines.mapped("pallet"))
                        product_container = sum(
                            product_lines.mapped("container")
                        )
                        product_brut = sum(product_lines.mapped("brut"))
                        product_pallet_weight = 0
                        product_container_weight = 0
                        for line in product_lines:
                            if line.move_id and line.move_id.production_id and line.move_id.production_id.pallet_id:
                                product_pallet_weight += line.move_id.production_id.pallet_id.weight * line.pallet
                            if line.move_id and line.move_id.production_id and line.move_id.production_id.packaging_id:
                                product_container_weight += line.move_id.production_id.packaging_id.weight * line.container
                        product_qty_done = sum(
                            product_lines.mapped("qty_done")
                        )
                        product_amount = sum(product_lines.mapped("amount"))
                        product_applied_price = (
                            (
                                product_amount / product_qty_done
                            ) if product_qty_done else 0
                        )
                        worksheet.write(n, m, product.product_id.default_code)
                        m += 1
                        worksheet.write(n, m, product.product_id.name)
                        m += 1
                        worksheet.write(n, m, product_pallet)
                        m += 1
                        worksheet.write(n, m, product_container)
                        m += 2
                        worksheet.write(n, m, product_brut, two_decimal_format)
                        m += 1
                        worksheet.write(n, m, product_pallet_weight, two_decimal_format)
                        m += 1
                        worksheet.write(n, m, product_container_weight, two_decimal_format)
                        m += 1
                        worksheet.write(n, m, product_qty_done, two_decimal_format)
                        m += 1
                        worksheet.write(
                            n, m, product_applied_price, three_decimal_format
                        )
                        m += 1
                        worksheet.write(
                            n, m, round(product_amount, 2), two_decimal_format
                        )
                        m += 2
                        worksheet.write(n, m, product_qty_done * 100 / sum(entry_movelines.mapped("qty_done")), two_decimal_format)
                n += 1
                m = 0
                worksheet.write(
                    n, m, line.product_category_id.display_name, result_int_format
                )
                m += 1
                worksheet.write(
                    n, m, "", result_int_format
                )
                m += 1
                worksheet.write(n, m, categ_pallet, result_int_format)
                m += 1
                worksheet.write(n, m, categ_container, result_int_format)
                m += 2
                worksheet.write(n, m, categ_brut, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_pallet_weight, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_container_weight, result_two_decimal)
                m += 1
                worksheet.write(n, m, categ_qty_done, result_two_decimal)
                m += 1
                worksheet.write(
                    n, m, categt_applied_price, result_three_decimal
                )
                m += 1
                worksheet.write(n, m, categ_amount, result_two_decimal)
                m += 2
                worksheet.write(n, m, categ_qty_done * 100 / sum(entry_movelines.mapped("qty_done")), result_two_decimal)
        n += 2
        m = 0
        worksheet.write(n, m, _("Total Entradas"), result_summary)
        m += 1
        worksheet.write(n, m, sum(entry_movelines.mapped("qty_done")), result_two_decimal)
        n += 1
        m = 0
        worksheet.write(n, m, _("Total Salidas"), result_summary)
        m += 1
        worksheet.write(n, m, sum(out_movelines.mapped("qty_done")), result_two_decimal)
        n += 1
        m = 0
        worksheet.write(n, m, _("Diferencia"), result_summary)
        m += 1
        worksheet.write(n, m, sum(entry_movelines.mapped("qty_done")) - sum(out_movelines.mapped("qty_done")), result_two_decimal)
