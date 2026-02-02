# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class QcTrigger(models.Model):
    _inherit = "qc.trigger"

    def get_manufacturing_trigger(self):
        cond = [
            ("company_id", "=", self.env.company.id),
            ("code", "=", "mrp_operation"),
        ]
        mrp_picking_type = self.env["stock.picking.type"].search(cond, limit=1)
        if not mrp_picking_type:
            return False
        cond = [
            ("company_id", "=", self.env.company.id),
            ("partner_selectable", "=", True),
            ("picking_type_id", "=", mrp_picking_type.id),
        ]
        qc_trigger_mrp = self.env["qc.trigger"].search(cond, limit=1)
        return qc_trigger_mrp
