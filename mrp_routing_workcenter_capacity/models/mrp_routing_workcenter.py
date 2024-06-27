# Copyright 2021 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, exceptions, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    capacity = fields.Float(
        string="Capacity",
        default=1.0,
    )
    time_start = fields.Float(
        string="Time before prod.",
        help="Time in minutes for the setup.",
    )
    time_stop = fields.Float(
        string="Time after prod.",
        help="Time in minutes for the cleaning.",
    )

    @api.depends("time_cycle_manual", "time_mode", "workorder_ids")
    def _compute_time_cycle(self):
        result = super(MrpRoutingWorkcenter, self)._compute_time_cycle()
        manual_ops = self.filtered(lambda operation: operation.time_mode == "manual")
        for operation in manual_ops:
            operation.time_cycle = operation.time_cycle_manual
        operations = self - manual_ops
        for operation in operations.filtered(lambda x: x.capacity):
            data = self.env["mrp.workorder"].read_group(
                [
                    ("operation_id", "=", operation.id),
                    ("qty_produced", ">", 0),
                    ("state", "=", "done"),
                ],
                ["operation_id", "duration", "qty_produced"],
                ["operation_id"],
                limit=operation.time_mode_batch,
            )
            count_data = {
                item["operation_id"][0]: (item["duration"], item["qty_produced"])
                for item in data
            }
            if count_data.get(operation.id) and count_data[operation.id][1]:
                operation.time_cycle = (
                    count_data[operation.id][0] / count_data[operation.id][1]
                ) * (operation.capacity or 1.0)
            else:
                operation.time_cycle = operation.time_cycle_manual
        return result

    @api.constrains("capacity")
    def _check_capacity(self):
        if any(routing_workcenter.capacity < 0.0 for routing_workcenter in self):
            raise exceptions.UserError(_("The capacity must be strictly positive."))
