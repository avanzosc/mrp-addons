# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class NestedNewLine(models.TransientModel):
    _name = "nested.new.line"
    _rec_name = "nested_id"

    nested_id = fields.Many2one(comodel_name="mrp.workorder.nest",
                                String="Nested Workorder")
    main_product_id = fields.Many2one(comodel_name="product.product",
                                      related="nested_id.main_product_id",
                                      string="Main Material")

    def action_done(self):
        workorders = self.env['mrp.workorder'].search([
            ('id', 'in', self._context.get('active_ids')),
            ('workcenter_id', '!=', False),
            ('state', '!=', 'done'),
        ])
        main_product_workcenter = {}
        for wo in workorders.filtered(lambda x: x.main_product_id):
            workcenter_dict = main_product_workcenter.get(
                wo.main_product_id.id)
            if workcenter_dict:
                workorders = workcenter_dict.get(wo.workcenter_id.id)
                if workorders:
                    workorders |= wo
                else:
                    workcenter_dict.update({wo.workcenter_id.id: wo})
            else:
                main_product_workcenter.update({wo.main_product_id.id: {
                    wo.workcenter_id.id: wo}})
        for main_id, workcenters in main_product_workcenter.items():
            for workcenter, wos in workcenters.items():
                new_lines = [(0, 0, {'workorder_id': wo.id}) for wo in wos]
                self.env['mrp.workorder.nest'].create({
                    'main_product_id': main_id,
                    'workcenter_id': workcenter,
                    'nested_line_ids': new_lines,
                })


