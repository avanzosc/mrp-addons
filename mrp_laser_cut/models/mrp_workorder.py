# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def _get_duration_expected(self, alternative_workcenter=False, ratio=1):
        self.ensure_one()
        laser_order = self.production_id.laser_cut_order_id
        if laser_order:
            quantity = self.qty_producing or self.qty_production
            return laser_order.time_per_unit * quantity
        return super()._get_duration_expected(
            alternative_workcenter=alternative_workcenter, ratio=ratio
        )
