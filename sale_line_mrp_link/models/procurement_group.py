# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        result = False
        if len(self) > 0 or not procurements:
            return super(ProcurementGroup, self).run(
                procurements, raise_user_error=raise_user_error)
        for procurement in procurements:
            if ("sale_line_id" not in procurement.values or not
                    procurement.values.get("sale_line_id", False)):
                result = super(ProcurementGroup, self).run(
                    [procurement], raise_user_error=raise_user_error)
            else:
                result = super(ProcurementGroup, self.with_context(
                    sale_line_id=procurement.values.get("sale_line_id"))).run(
                        [procurement], raise_user_error=raise_user_error)
        return result
