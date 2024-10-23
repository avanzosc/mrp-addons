from odoo import models
from odoo.tools import float_round


class ReportBomStructurePrecision(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_bom(
        self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False
    ):
        bom = self.env["mrp.bom"].browse(bom_id)
        company = bom.company_id or self.env.company
        bom_quantity = line_qty
        if line_id:
            current_line = self.env["mrp.bom.line"].browse(int(line_id))
            bom_quantity = (
                current_line.product_uom_id._compute_quantity(
                    line_qty, bom.product_uom_id
                )
                or 0
            )
        # Display bom components for current selected product variant
        if product_id:
            product = self.env["product.product"].browse(int(product_id))
        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
        if product:
            price = (
                product.uom_id._compute_price(
                    product.with_company(company).standard_price, bom.product_uom_id
                )
                * bom_quantity
            )
            attachments = self.env["mrp.document"].search(
                [
                    "|",
                    "&",
                    ("res_model", "=", "product.product"),
                    ("res_id", "=", product.id),
                    "&",
                    ("res_model", "=", "product.template"),
                    ("res_id", "=", product.product_tmpl_id.id),
                ]
            )
        else:
            # Use the product template instead of the variant
            price = (
                bom.product_tmpl_id.uom_id._compute_price(
                    bom.product_tmpl_id.with_company(company).standard_price,
                    bom.product_uom_id,
                )
                * bom_quantity
            )
            attachments = self.env["mrp.document"].search(
                [
                    ("res_model", "=", "product.template"),
                    ("res_id", "=", bom.product_tmpl_id.id),
                ]
            )
        operations = self._get_operation_line(
            bom,
            float_round(bom_quantity, precision_rounding=1, rounding_method="UP"),
            0,
        )
        lines = {
            "bom": bom,
            "bom_qty": bom_quantity,
            "bom_prod_name": product.display_name,
            "currency": company.currency_id,
            "product": product,
            "code": bom and bom.display_name or "",
            "price": round(price, 4),  # Set precision to 4 decimals for price
            "total": sum([op["total"] for op in operations]),
            "level": level or 0,
            "operations": operations,
            "operations_cost": sum([op["total"] for op in operations]),
            "attachments": attachments,
            "operations_time": sum([op["duration_expected"] for op in operations]),
        }
        components, total = self._get_bom_lines(
            bom, bom_quantity, product, line_id, level
        )
        lines["components"] = components
        lines["total"] += total
        return lines

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components = []
        total = 0
        for line in bom.bom_line_ids:
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            company = bom.company_id or self.env.company
            price = (
                line.product_id.uom_id._compute_price(
                    line.product_id.with_company(company).standard_price,
                    line.product_uom_id,
                )
                * line_quantity
            )
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(
                    line_quantity, line.child_bom_id.product_uom_id
                )
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = self.env.company.currency_id.round(sub_total)
            components.append(
                {
                    "prod_id": line.product_id.id,
                    "prod_name": line.product_id.display_name,
                    "code": line.child_bom_id and line.child_bom_id.display_name or "",
                    "prod_qty": line_quantity,
                    "prod_uom": line.product_uom_id.name,
                    "prod_cost": round(
                        price, 4
                    ),  # Set precision to 4 decimals for price
                    "parent_id": bom.id,
                    "line_id": line.id,
                    "level": level or 0,
                    "total": sub_total,
                    "child_bom": line.child_bom_id.id,
                    "phantom_bom": line.child_bom_id
                    and line.child_bom_id.type == "phantom"
                    or False,
                    "attachments": self.env["mrp.document"].search(
                        [
                            "|",
                            "&",
                            ("res_model", "=", "product.product"),
                            ("res_id", "=", line.product_id.id),
                            "&",
                            ("res_model", "=", "product.template"),
                            ("res_id", "=", line.product_id.product_tmpl_id.id),
                        ]
                    ),
                }
            )
            total += sub_total
        return components, total
