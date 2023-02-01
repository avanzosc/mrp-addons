# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_generate_serial(self):
        return super(MrpProduction, self.with_context(
            lot_by_category=True)).action_generate_serial()
