# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    def _get_new_mo_values(self, origin_manufacture_order, analytic_account):
        res = super()._get_new_mo_values(origin_manufacture_order,
                                         analytic_account)
        res.update({'sale_line_id': origin_manufacture_order.sale_line_id.id})
        return res
