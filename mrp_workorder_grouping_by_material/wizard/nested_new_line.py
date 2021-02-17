# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class NestedNewLine(models.TransientModel):
    _name = "nested.new.line"
    _rec_name = "nest_code"

    nest_code = fields.Char(string="Nest Name")

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
                res_workorders = workcenter_dict.get(
                    wo.workcenter_id.id, self.env['mrp.workorder'])
                res_workorders |= wo
                workcenter_dict.update({wo.workcenter_id.id: res_workorders})
            else:
                main_product_workcenter.update({wo.main_product_id.id: {
                    wo.workcenter_id.id: wo}})
        for main_id, workcenters in main_product_workcenter.items():
            for workcenter, wos in workcenters.items():
                new_lines = [(0, 0, {'workorder_id': wo.id}) for wo in wos]
                self.env['mrp.workorder.nest'].create({
                    'code': self.nest_code,
                    'main_product_id': main_id,
                    'workcenter_id': workcenter,
                    'nested_line_ids': new_lines,
                })


