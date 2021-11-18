# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _compute_workorder_count(self):
        for production in self:
            production.workorder_count = len(production.workorder_ids)

    workorder_count = fields.Integer(
        '# Work Orders', compute='_compute_workorder_count')

    def action_view_workorder(self):
        context = self.env.context.copy()
        context.update({'default_production_id': self.id})
        return {
            'name': _("Work Orders"),
            'view_mode': 'tree,form',
            'res_model': 'mrp.workorder',
            'domain': [('id', 'in', self.workorder_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': context
        }
