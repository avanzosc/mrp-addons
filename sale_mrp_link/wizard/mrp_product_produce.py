# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, exceptions, _


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"


    def do_produce(self):
        res = super().do_produce
        make_to_order = self.env.ref(
            'stock.route_warehouse0_mto', False)
        for line in self.production_id.product_line_ids.filtered(
                lambda x: make_to_order in x.product_id.route_ids):
            line._action_launch_stock_rule()
        return res