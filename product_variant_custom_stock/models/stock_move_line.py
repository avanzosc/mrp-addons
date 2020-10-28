# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_version_id = fields.Many2one(comodel_name="product.version",
                                         related="move_id.product_version_id",
                                         store="True")

    real_in = fields.Float(string="Real In",
                           compute="_compute_move_in_out_qty", store="True")
    real_out = fields.Float(string="Real Out",
                            compute="_compute_move_in_out_qty", store="True")
    virtual_in = fields.Float(string="Virtual In",
                              compute="_compute_move_in_out_qty", store="True")
    virtual_out = fields.Float(string="Virtual Out",
                               compute="_compute_move_in_out_qty",
                               store="True")

    api.depends("location_id", "location_dest_id", "product_qty")
    def _compute_move_in_out_qty(self):
        for move in self:
            move.real_in = 1
            move.real_out = 2
            move.virtual_in = 3
            move.virtual_out = 4
