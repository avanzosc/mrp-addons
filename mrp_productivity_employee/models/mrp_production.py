# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        return super(
            MrpProduction, self.with_context(from_button_mark_done=True)
        ).button_mark_done()
