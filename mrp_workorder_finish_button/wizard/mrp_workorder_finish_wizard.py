# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _


class MrpWorkorderFinishWizard(models.TransientModel):
    _name = 'mrp.workorder.finish.wizard'
    _description = 'Wizard to finish a work order'

    text = fields.Char(
        default=_('This work order has outstanding inventory movements. ' +
                  'You want to:'), readonly=True)

    def button_generate_assign(self):
        workorder = self.env['mrp.workorder'].browse(
            self.env.context.get('active_id'))
        for move in workorder.stock_move_ids:
            if move.state in ('draft', 'confirmed'):
                move._action_assign()
        workorder.button_finish()

    def button_generate_unreserve(self):
        workorder = self.env['mrp.workorder'].browse(
            self.env.context.get('active_id'))
        for move in workorder.stock_move_ids:
            if move.state in ('draft', 'confirmed', 'partially_available'):
                move.write({'state': 'cancel'})
        workorder.button_finish()
