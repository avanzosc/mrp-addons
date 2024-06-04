# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime

from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def get_date_now(self):
        return datetime.now().strftime("%d/%m/%Y")

    def _get_children(self, bom_line_ids, level=0):
        result = []

        def _get_rec(bom_line_ids, level):
            for line in bom_line_ids:
                res = line.get_datas_to_print_bom()
                result.append(res)
                if line.child_line_ids:
                    if level < 6:
                        level += 1
                    _get_rec(line.child_line_ids, level)
                    if 6 > level > 0:
                        level -= 1
            return result

        return _get_rec(bom_line_ids, level)
