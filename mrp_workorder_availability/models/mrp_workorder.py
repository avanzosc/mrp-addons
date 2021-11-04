# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def _compute_count_stock_move(self):
        for workorder in self:
            workorder.count_stock_move = len(workorder.stock_move_ids)

    def _compute_count_move_line(self):
        for workorder in self:
            workorder.count_move_line = len(workorder.move_line_ids)

    stock_move_ids = fields.One2many(
        string='Stock Moves', comodel_name='stock.move',
        inverse_name='workorder_id')
    count_stock_move = fields.Integer(
        '# Stock Moves', compute='_compute_count_stock_move')
    count_move_line = fields.Integer(
        '# Stock Move Lines', compute='_compute_count_move_line')

    def action_view_stock_move(self):
        context = self.env.context.copy()
        context.update({'default_workorder_id': self.id})
        return {
            'name': _("Stock Moves"),
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            "views": [[self.env.ref(
                'stock.view_move_tree').id, "tree"],
                [False, "form"]],
            'domain': [('id', 'in', self.stock_move_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': context,
        }

    def action_view_stock_move_line(self):
        context = self.env.context.copy()
        context.update({'default_workorder_id': self.id})
        return {
            'name': _("Stock Move Lines"),
            'view_mode': 'tree,form',
            'res_model': 'stock.move.line',
            "views": [[self.env.ref(
                'stock.view_move_line_tree').id, "tree"],
                [False, "form"]],
            'domain': [('id', 'in', self.move_line_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': context,
        }

    def action_assign(self):
        for workorder in self:
            workorder.stock_move_ids._action_assign()

    def action_unreserve(self):
        for workorder in self:
            workorder.stock_move_ids._do_unreserve()

    def action_done(self):
        for workorder in self:
            workorder.stock_move_ids._action_done()

    def action_cancel(self):
        for workorder in self:
            workorder.stock_move_ids.filtered(lambda x: x.state not in (
                'cancel', 'done'))._action_cancel()
