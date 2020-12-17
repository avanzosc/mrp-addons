# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.models import expression
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def _generate_final_lot_ids(self, final_lot):
        """ Generate stock move lines """
        self.ensure_one()
        MoveLine = self.env['stock.move.line']
        tracked_moves = self.move_raw_ids.filtered(
            lambda move: move.state not in ('done', 'cancel') and move.product_id.tracking != 'none' and move.product_id != self.production_id.product_id and move.bom_line_id)
        for move in tracked_moves:
            qty = move.unit_factor * self.qty_producing
            if move.product_id.tracking == 'serial':
                while float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                    MoveLine.create({
                        'move_id': move.id,
                        'product_uom_qty': 0,
                        'product_uom_id': move.product_uom.id,
                        'qty_done': min(1, qty),
                        'production_id': self.production_id.id,
                        'workorder_id': self.id,
                        'product_id': move.product_id.id,
                        'done_wo': False,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'lot_produced_id': final_lot.id,
                    })
                    qty -= 1
            else:
                MoveLine.create({
                    'move_id': move.id,
                    'product_uom_qty': 0,
                    'product_uom_id': move.product_uom.id,
                    'qty_done': qty,
                    'product_id': move.product_id.id,
                    'production_id': self.production_id.id,
                    'workorder_id': self.id,
                    'done_wo': False,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'lot_produced_id': final_lot.id,
                    })

    @api.multi
    def _create_serial_lot(self, suffix):
        lot_name = "{}-{}".format(self.production_id.name, suffix)
        lot_obj = self.env['stock.production.lot']
        lot_id = lot_obj.search([("name", "=", lot_name)])
        if lot_id:
            return lot_id
        return self.env['stock.production.lot'].create(
            {'name': lot_name,
             'product_id': self.production_id.product_id.id})

    # @api.multi
    # def button_execute_all_moves(self):
    #     for order in self:
    #         lot_incremental = 0
    #         while (order.qty_production != order.qty_produced or
    #                order.state != 'done' and not order.final_lot_id):
    #             lot_incremental += 1
    #             serial_lot = order._create_serial_lot(lot_incremental)
    #             order.final_lot_id = serial_lot
    #             order.all_record_production()
    #             order._make_active_moves()
    @api.multi
    def button_start(self):
        res = super().button_start()
        if self.move_raw_ids:
            final_lots = self.generate_lots()
            self.final_lot_id = final_lots[int(self.qty_produced)]

        #self.button_create_all_moves()
        return res

    @api.multi
    def button_execute_all_moves(self):
        for order in self:
            if not self.move_raw_ids:
                order.qty_produced = order.production_id.product_qty
                order.button_finish()
                continue
            order.all_record_production()
            order._make_active_moves()
            order.final_workorder()
            order.qty_produced += order.qty_producing
            rounding = order.production_id.product_uom_id.rounding
            if float_compare(order.qty_produced, order.production_id.product_qty,
                             precision_rounding=rounding) >= 0:
                order.button_finish()


    @api.multi
    def generate_lots(self):
        lot_incremental = 0
        serial_lot = self.env['stock.production.lot']
        i=0
        while (self.qty_production - i > 0):
            lot_incremental += 1
            serial_lot |= self._create_serial_lot(lot_incremental)
            i += 1
        return serial_lot

    @api.multi
    def record_production(self):
        final_lots = self.generate_lots()
        super().record_production()
        if self.state == 'progress':
            self.final_lot_id = final_lots[int(self.qty_produced)]
        

    @api.multi
    def button_create_all_moves(self):
        for order in self:
            i = 1
            final_lots = order.generate_lots()
            active_moves = order.active_move_line_ids.filtered(
                lambda x: x.product_id.tracking != 'none')
            for active_move in active_moves:
                active_move.lot_produced_id = final_lots[0].id
            while (order.qty_production - i > 0):
                order._generate_final_lot_ids(final_lots[i])
                i += 1

    @api.multi
    def all_record_production(self):
        if not self:
            return True

        self.ensure_one()
        if self.qty_producing <= 0:
            raise UserError(_('Please set the quantity you are currently producing. It should be different from zero.'))

        generated_lots = self.env['stock.production.lot']
        if (self.production_id.product_id.tracking != 'none') and not self.final_lot_id and self.move_raw_ids:
            generated_lots = self.generate_lots()

        # Update quantities done on each raw material line
        # For each untracked component without any 'temporary' move lines,
        # (the new workorder tablet view allows registering consumed quantities for untracked components)
        # we assume that only the theoretical quantity was used
        for lot in generated_lots:
            for move in self.move_raw_ids:
                if move.has_tracking == 'none' and (move.state not in ('done', 'cancel')) and move.bom_line_id\
                            and move.unit_factor and not move.move_line_ids.filtered(lambda ml: not ml.done_wo):
                    rounding = move.product_uom.rounding
                    if self.product_id.tracking != 'none':
                        qty_to_add = float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)
                        move._generate_consumed_move_line(qty_to_add, lot)
                    elif len(move._get_move_lines()) < 2:
                        move.quantity_done += float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)
                    else:
                        move._set_quantity_done(move.quantity_done + float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding))
        return True


    def _make_active_moves(self):
        # Transfer quantities from temporary to final move lots or make them final
        for move_line in self.active_move_line_ids:
            # Check if move_line already exists
            if move_line.qty_done <= 0:  # rounding...
                move_line.sudo().unlink()
                continue
            if move_line.product_id.tracking != 'none' and not move_line.lot_id:
                raise UserError(_(
                    'You should provide a lot/serial number for a component.'))
            # Search other move_line where it could be added:
            lots = self.move_line_ids.filtered(
                lambda x: (x.lot_id.id == move_line.lot_id.id) and (
                    not x.lot_produced_id) and (not x.done_move) and (
                                      x.product_id == move_line.product_id))
            if lots:
                lots[0].qty_done += move_line.qty_done
                #lots[0].lot_produced_id = self.final_lot_id
                self._link_to_quality_check(move_line, lots[0])
                move_line.sudo().unlink()
            else:
                #move_line.lot_produced_id = self.final_lot_id
                move_line.done_wo = True

        # self.move_line_ids.filtered(
        #     lambda move_line: not move_line.done_move and not move_line.lot_produced_id and move_line.qty_done > 0
        # ).write({
        #     'lot_produced_id': self.final_lot_id.id,
        #     'lot_produced_qty': self.qty_producing
        # })

    def final_workorder(self):
        # If last work order, then post lots used
        # TODO: should be same as checking if for every workorder something has been done?
        generated_lots = self.generate_lots()
        if not self.next_work_order_id:
            production_move = self.production_id.move_finished_ids.filtered(
                                lambda x: (x.product_id.id == self.production_id.product_id.id) and (x.state not in ('done', 'cancel')))
            if production_move.product_id.tracking != 'none':
                move_line = production_move.move_line_ids.filtered(lambda x:
                                                                   x.lot_id.id in generated_lots)
                if move_line:
                    for line in move_line:
                        move_line.product_uom_qty = self.qty_production
                        move_line.qty_done = self.qty_production
                else:
                    for lot in generated_lots:
                        location_dest_id = production_move.location_dest_id.get_putaway_strategy(self.product_id).id or production_move.location_dest_id.id
                        move_line.create({'move_id': production_move.id,
                                 'product_id': production_move.product_id.id,
                                 'lot_id': lot.id,
                                 'product_uom_qty': self.qty_producing,
                                 'product_uom_id': production_move.product_uom.id,
                                 'qty_done': self.qty_producing,
                                 'workorder_id': self.id,
                                 'location_id': production_move.location_id.id,
                                 'location_dest_id': location_dest_id,
                        })
            else:
                production_move._set_quantity_done(self.qty_production)

        if not self.next_work_order_id:
            for by_product_move in self._get_byproduct_move_to_update():
                    if by_product_move.has_tracking != 'serial':
                        values = self._get_byproduct_move_line(by_product_move, self.qty_production * by_product_move.unit_factor)
                        self.env['stock.move.line'].create(values)
                    elif by_product_move.has_tracking == 'serial':
                        qty_todo = by_product_move.product_uom._compute_quantity(self.qty_production * by_product_move.unit_factor, by_product_move.product_id.uom_id)
                        for i in range(0, int(float_round(qty_todo, precision_digits=0))):
                            values = self._get_byproduct_move_line(by_product_move, 1)
                            self.env['stock.move.line'].create(values)

        # # Update workorder quantity produced
        # self.qty_produced += self.qty_producing
        #
        # if self.final_lot_id:
        #     self.final_lot_id.use_next_on_work_order_id = self.next_work_order_id
        #     self.final_lot_id = False
        #
        # # One a piece is produced, you can launch the next work order
        # self._start_nextworkorder()
        #
        # # Set a qty producing
        # rounding = self.production_id.product_uom_id.rounding
        # if float_compare(self.qty_produced, self.production_id.product_qty, precision_rounding=rounding) >= 0:
        #     self.qty_producing = 0
        # elif self.production_id.product_id.tracking == 'serial':
        #     self._assign_default_final_lot_id()
        #     self.qty_producing = 1.0
        #     self._generate_lot_ids()
        # else:
        #     self.qty_producing = float_round(self.production_id.product_qty - self.qty_produced, precision_rounding=rounding)
        #     self._generate_lot_ids()
        #
        # if self.next_work_order_id and self.next_work_order_id.state not in ['done', 'cancel'] and self.production_id.product_id.tracking != 'none':
        #     self.next_work_order_id._assign_default_final_lot_id()

        # if float_compare(self.qty_produced, self.production_id.product_qty, precision_rounding=rounding) >= 0:
        #     self.button_finish()
        return True

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
