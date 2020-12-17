# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _has_parent(self, parent_location):
        if not self.location_id:
            return False
        elif self.location_id == parent_location:
            return True
        else:
            return self.location_id._has_parent(parent_location)
