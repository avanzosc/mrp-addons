# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    force_lot_name = fields.Char("Lot Name")
    display_force_name = fields.Boolean(compute="_compute_force_field")

    @api.depends('force_lot_name')
    def _compute_force_field(self):
        for order in self:
            product = order.product_id
            order.display_force_name = product.categ_id.force_lot_name \
                and product.tracking != 'none'

    def record_production(self):
        for order in self:
            if order.display_force_name and order.final_lot_id:
                order.final_lot_id.name = order.force_lot_name
                order.force_lot_name = ""
        return super().record_production()
