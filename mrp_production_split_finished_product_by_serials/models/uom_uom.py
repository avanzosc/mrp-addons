# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class UomUom(models.Model):
    _inherit = "uom.uom"

    def _compute_quantity(self, qty, to_unit, round=True, rounding_method='UP',
                          raise_if_failure=True):
        if "qty_twith_serial" in self.env.context:
            return super(UomUom, self)._compute_quantity(
                self.env.context.get("qty_twith_serial"), to_unit, round=round,
                rounding_method=rounding_method,
                raise_if_failure=raise_if_failure)
        else:
            return super(UomUom, self)._compute_quantity(
                qty, to_unit, round=round, rounding_method=rounding_method,
                raise_if_failure=raise_if_failure)
