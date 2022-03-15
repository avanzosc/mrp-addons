# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _prepare_subcontract_mo_vals(self, subcontract_move, bom):
        subcontract_move.ensure_one()
        vals = super(StockPicking, self)._prepare_subcontract_mo_vals(
            subcontract_move, bom)
        vals.update({
            "state": "confirmed",
            "active": True,
        })
        return vals
