# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.models import expression
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    @api.multi
    def generate_lot(self, suffix):
        lot_name = "{}-{}".format(self.production_id.name, suffix)
        lot_obj = self.env['stock.production.lot']
        lot_id = lot_obj.search([("name", "=", lot_name)])
        if lot_id:
            return lot_id
        return self.env['stock.production.lot'].create(
            {'name': lot_name,
             'product_id': self.production_id.product_id.id})

    @api.multi
    def button_start(self):
        res = super().button_start()
        if self.move_raw_ids:
            self.final_lot_id = self.generate_lot(self.qty_produced)
        return res

    @api.multi
    def record_production(self):
        if not self.move_raw_ids:
            self.qty_produced = self.production_id.product_qty
            self.button_finish()
        super().record_production()
        if self.state == 'progress' and self.product_id.tracking != 'none':
            self.final_lot_id = self.generate_lot(self.qty_produced)

    @api.multi
    def button_open_active_move_lines(self):
        self.ensure_one()
        self = self.with_context(
            default_workorder_id=self.id)
        action = self.env.ref('stock.stock_move_line_action')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].pop('search_default_done', False)
        action_dict['context'].pop('search_default_groupby_product_id', False)
        action_dict['context'].update({
            'default_workorder_id': self.id,
            'search_default_groupby_lot_produced_id': 1,
        })
        domain = expression.AND([
            [('workorder_id', '=', self.id)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict

    def button_open_lots(self):
        self.ensure_one()
        location_obj = self.env['stock.location']
        physical_location = location_obj.search(
            [('name', '=', 'Physical Locations')])
        virtual_location = location_obj.search(
                    [('name', '=', 'Virtual Locations')])
        move_lines = self.active_move_line_ids | self.move_line_ids
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

