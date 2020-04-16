# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    moves_to_consume_count = fields.Integer(
        string='Counter movements to consume', store=True,
        compute='_compute_moves_to_consume_count')

    @api.depends('move_raw_ids', 'move_raw_ids.scrapped')
    def _compute_moves_to_consume_count(self):
        for production in self.filtered(
                lambda c: c.move_raw_ids):
            moves = production.mapped('move_raw_ids').filtered(
                lambda x: not x.scrapped)
            production.moves_to_consume_count = len(moves) if moves else 0

    @api.multi
    def button_show_moves_to_consume(self):
        self.ensure_one()
        moves = self.mapped('move_raw_ids').filtered(
            lambda x: not x.scrapped)
        action = self.env.ref(
            'mrp_usability.action_show_productions_moves_to_consume')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].update(
            {'search_default_production_id': self.id,
             'default_production_id': self.id})
        domain = expression.AND([
            [('id', 'in', moves.ids)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict if moves else True
