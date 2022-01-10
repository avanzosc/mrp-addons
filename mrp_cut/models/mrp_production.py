# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.onchange("product_qty")
    def onchange_qty_pieces_cut(self):
        for line in self.move_raw_ids:
            line.qty_pieces_cut = self.product_qty * line.qty_pieces_set
