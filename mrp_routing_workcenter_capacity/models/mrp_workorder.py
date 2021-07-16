# Copyright 2021 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models
from odoo.tools import float_round


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def _get_duration_expected(self, alternative_workcenter=False, ratio=1):
        self.ensure_one()
        if not self.workcenter_id and not self.operation_id:
            return super(MrpWorkorder, self)._get_duration_expected(
                alternative_workcenter=alternative_workcenter, ratio=ratio)
        qty_production = self.production_id.product_uom_id._compute_quantity(
            self.qty_production, self.production_id.product_id.uom_id)
        capacity = (
            self.operation_id.capacity if self.operation_id.capacity else
            self.workcenter_id.capacity)
        cycle_number = float_round(qty_production / capacity,
                                   precision_digits=0, rounding_method='UP')
        if self.operation_id.time_start or self.operation_id.time_stop:
            time_start = self.operation_id.time_start
            time_stop = self.operation_id.time_stop
        else:
            time_start = self.workcenter_id.time_start
            time_stop = self.workcenter_id.time_stop
        if alternative_workcenter:
            duration_expected_working = (
                (self.duration_expected - time_start - time_stop) *
                self.workcenter_id.time_efficiency / (100.0 * cycle_number))
            if duration_expected_working < 0:
                duration_expected_working = 0
            return (alternative_workcenter.time_start +
                    alternative_workcenter.time_stop +
                    cycle_number * duration_expected_working * 100.0 /
                    alternative_workcenter.time_efficiency)
        time_cycle = self.operation_id and self.operation_id.time_cycle or 60.0
        return (time_start + time_stop + cycle_number * time_cycle * 100.0 /
                self.workcenter_id.time_efficiency)
