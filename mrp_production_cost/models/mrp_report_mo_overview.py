# Copyright 2026 Berezi Amubieta
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class MrpReportMoOverview(models.AbstractModel):
    _inherit = "report.mrp.report_mo_overview"

    def _can_show_costs(self):
        return self.env.user.has_group("product_cost_security.group_product_cost")

    @api.model
    def _get_report_data(self, production_id):
        res = super()._get_report_data(production_id)

        # Indicamos al componente JS si el usuario puede ver costes.
        res["show_costs"] = self._can_show_costs()

        return res

    def _include_pdf_specifics(self, doc, data=None):
        doc = super()._include_pdf_specifics(doc, data=data)

        # Impedir que el PDF muestre costes aunque el usuario
        # manipule los parámetros de impresión.
        if not self._can_show_costs():
            doc["show_mo_costs"] = False
            doc["show_real_costs"] = False
            doc["show_bom_costs"] = False
            doc["show_unit_costs"] = False

        return doc
