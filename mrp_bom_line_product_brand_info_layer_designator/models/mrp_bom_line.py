# -*- coding: utf-8 -*-
# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def get_datas_to_print_bom(self):
        res = super(MrpBomLine, self).get_datas_to_print_bom()
        res["layer"] = self.layer
        res["designator"] = self.designator
        return res
