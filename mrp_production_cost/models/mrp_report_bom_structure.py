# Copyright 2026 Berezi Amubieta
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class MrpReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _can_show_costs(self):
        return self.env.user.has_group("product_cost_security.group_product_cost")

    @api.model
    def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
        res = super()._get_report_data(
            bom_id,
            searchQty=searchQty,
            searchVariant=searchVariant,
        )

        # `res["lines"]` es lo que recibe BomOverviewTable como `data`
        res["lines"]["show_costs"] = self._can_show_costs()

        return res

    @api.model
    def _get_pdf_doc(self, bom_id, data, quantity, product_variant_id=None):
        doc = super()._get_pdf_doc(
            bom_id,
            data,
            quantity,
            product_variant_id=product_variant_id,
        )

        # Respeta tanto el checkbox/opción estándar de Odoo
        # como nuestro grupo de seguridad.
        doc["show_costs"] = doc.get("show_costs", False) and self._can_show_costs()

        return doc
