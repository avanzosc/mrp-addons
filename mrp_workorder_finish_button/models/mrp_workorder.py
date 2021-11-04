# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_finish(self):
        for workorder in self:
            if any(m.state in (
                'draft', 'waiting', 'confirmed', 'partially_available') for (
                    m) in workorder.stock_move_ids):
                wiz_obj = self.env['mrp.workorder.finish.wizard']
                wiz = wiz_obj.with_context({
                    'active_id': self.id,
                    'active_model': 'mrp.workorder'}).create({})
                context = self.env.context.copy()
                context.update({
                    'active_id': self.id,
                    'active_model': 'mrp.workorder'})
                return {'name': _('Finish Work Order'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'mrp.workorder.finish.wizard',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_id': wiz.id,
                        'target': 'new',
                        'context': context}
            else:
                return super(MrpWorkorder, self).button_finish()
