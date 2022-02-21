# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class RepairLine(models.Model):
    _inherit = 'repair.line'

    @api.multi
    @api.onchange('type', 'repair_id', 'repair_id.type_id')
    def onchange_operation_type(self):
        super(RepairLine, self).onchange_operation_type()
        if self.type == 'add':
            self.location_id = self.repair_id.type_id.location_id.id
            self.location_dest_id = self.repair_id.type_id.location_dest_id.id
        else:
            self.location_id = self.repair_id.type_id.location_dest_id.id
            self.location_dest_id = self.repair_id.type_id.location_id.id
