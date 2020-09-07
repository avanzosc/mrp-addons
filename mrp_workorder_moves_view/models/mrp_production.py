# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.tools.safe_eval import safe_eval
from odoo.models import expression

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def button_open_lots(self):
        self.ensure_one()
        location_obj = self.env['stock.location']
        physical_location = location_obj.search(
            [('name', '=', 'Physical Locations')])
        virtual_location = location_obj.search(
                    [('name', '=', 'Virtual Locations')])
        move_lines = self.env['stock.move.line']
        for workorder in self.env['mrp.workorder'].search(
                [('production_id', '=', self.id)]):
            move_lines |= workorder.active_move_line_ids
            move_lines |= workorder.move_line_ids
        produce_lines = move_lines.filtered(
            lambda x: x.location_id._has_parent(virtual_location) and
            x.location_dest_id._has_parent(physical_location))
        produce_lots = produce_lines.mapped('lot_id')
        action = self.env.ref('stock.action_production_lot_form')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].pop('search_default_group_by_product', False)
        action_dict['context'].update({
            'default_workorder_id': self.id,
        })
        action_dict['ids'] = produce_lots
        domain = expression.AND([
            [('id', 'in', produce_lots.ids)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict
