# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, exceptions, _


class StockPicking(models.Model):
    _inherit = "stock.move"

    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Product Version",
                                         compute="_compute_product_version")

    @api.depends('custo')

    # @api.multi
    # def button_validate(self):
    #     res = super().button_validate()
    #     for move in self.move_line_ids:
    #         if not move.lot_id.product_version_id:
    #             pass