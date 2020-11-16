# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class NestedNewLine(models.TransientModel):
    _name = "nested.new.line"
    _rec_name = "nested_id"

    nested_id = fields.Many2one(comodel_name="mrp.workorder.nest",
                                String="Nested Workorder")
    main_product_id = fields.Many2one(comodel_name="product.product",
                                      related="nested_id.main_product_id",
                                      string="Main Material")

    @api.multi
    def action_done(self):
        added_wo = self.nested_id.nested_line_ids.mapped('workorder_id')
        workorders = self.env['mrp.workorder'].search([
            ('id', 'in', self._context.get('active_ids')),
            ('id', 'not in', added_wo),
            ('main_product_id', '=', self.nested_id.main_product_id.id)
            ('state', '!=', 'done'),
        ])
        new_lines = []
        for wo in workorders:
            new_lines.append((0, 0, {
                "workorder_id": wo.id,
            }))
        self.nested_id.write({'nested_line_ids': new_lines})
