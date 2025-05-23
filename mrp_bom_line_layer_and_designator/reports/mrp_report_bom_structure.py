# Copyright 2024 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_bom_data(
        self,
        bom,
        warehouse,
        product=False,
        line_qty=False,
        bom_line=False,
        level=0,
        parent_bom=False,
        index=0,
        product_info=False,
        ignore_stock=False,
    ):
        res = super()._get_bom_data(
            bom,
            warehouse,
            product=product,
            line_qty=line_qty,
            bom_line=bom_line,
            level=level,
            parent_bom=parent_bom,
            index=index,
            product_info=product_info,
            ignore_stock=ignore_stock,
        )
        line_ids = self.env["mrp.bom.line"].search([("bom_id", "=", bom.id)])
        for line in res["components"]:
            bom_line = line_ids.filtered(
                lambda ln: ln.product_id.display_name == line["name"]
                and ln.product_qty == line["quantity"]
            )
            if len(bom_line) > 1:
                bom_line = self._find_untreated(bom_line, res)
            line.update(
                {
                    "layer": bom_line.layer or "",
                    "designator": bom_line.designator or "",
                }
            )
        # if parent_bom and parent_bom.location_id.complete_name:
        #     res["location"] = parent_bom.location_id.complete_name
        # else:
        #     res["location"] = bom.location_id.complete_name or ""
        return res

    # @api.model
    # def _get_component_data(
    #     self,
    #     parent_bom,
    #     warehouse,
    #     bom_line,
    #     line_quantity,
    #     level,
    #     index,
    #     product_info,
    #     ignore_stock=False,
    # ):
    #     res = super(BomStructureReport, self)._get_component_data(
    #         parent_bom,
    #         warehouse,
    #         bom_line,
    #         line_quantity,
    #         level,
    #         index,
    #         product_info,
    #         ignore_stock=ignore_stock,
    #     )
    #     # line_ids = self.env["mrp.bom.line"].search([("bom_id", "=", parent_bom.id)])
    #     res["location"] = parent_bom.location_id.complete_name or ""
    #     return res

    @api.model
    def _get_pdf_line(
        self, bom_id, product_id=False, qty=1, unfolded_ids=None, unfolded=False
    ):
        res = super()._get_pdf_line(bom_id, product_id, qty, unfolded_ids, unfolded)
        line_ids = self.env["mrp.bom.line"].search([("bom_id", "=", bom_id)])
        for line in res["lines"]:
            line_id = line_ids.filtered(
                lambda ln: ln.product_id.display_name == line["name"]
                and ln.product_qty == line["quantity"]
            )
            if len(line_id) > 1:
                line_id = self._find_untreated(line_id, res)
            line.update(
                {
                    "layer": line_id.layer or "",
                    "designator": line_id.designator or "",
                }
            )
        return res

    def _find_untreated(self, bom_lines, res):
        for bom_line in bom_lines:
            bom_line_treated = self.env["mrp.bom.line"]
            for line in res["components"]:
                if (
                    line["name"] == bom_line.product_id.display_name
                    and line["quantity"] == bom_line.product_qty
                    and "layer" in line
                    and bom_line.layer == line.get("layer")
                    and "designator" in line
                    and bom_line.designator == line.get("designator")
                ):
                    bom_line_treated += bom_line
            if not bom_line_treated:
                return bom_line
