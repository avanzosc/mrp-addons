# Copyright 2014 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_lots_mrp_production_report(self):
        lots = ""
        lines = self.move_line_ids.filtered(lambda x: x.lot_id)
        for line in lines:
            lots = (
                line.lot_id.name
                if not lots
                else "{}, {}".format(lots, line.lot_id.name)
            )
        return lots
