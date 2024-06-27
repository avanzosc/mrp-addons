# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpWorkorderPendingWizard(models.TransientModel):
    _inherit = "mrp.workorder.pending.wizard"

    def button_create_claim(self):
        if self.loss_id:
            workorder = self.env["mrp.workorder"].browse(
                self.env.context.get("active_id")
            )
            if workorder.time_ids:
                mrp_workcenter_productivity = max(
                    workorder.time_ids, key=lambda x: x.date_end
                )
                mrp_workcenter_productivity.loss_id = self.loss_id.id
        return super(MrpWorkorderPendingWizard, self).button_create_claim()
