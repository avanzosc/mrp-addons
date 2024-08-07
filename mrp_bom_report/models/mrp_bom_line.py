# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def get_datas_to_print_bom(self):
        res = {}
        res["product_name"] = self.product_id.display_name
        res["product_qty"] = self.product_qty
        operation = self.operation_id.name if self.operation_id else ""
        res["operation"] = operation
        return res
