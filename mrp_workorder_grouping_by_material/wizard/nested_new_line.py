# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class NestedNewLine(models.TransientModel):
    _name = "nested.new.line"
    _rec_name = "nest_code"

    nest_code = fields.Char(string="Nest Name")
    product_id = fields.Many2one(comodel_name='product.product')
    possible_product_ids = fields.Many2many(comodel_name="product.product")
    line_ids = fields.One2many(comodel_name="nested.lines.info",
                               inverse_name="nest_id", string="Nest Lines")

    def _workorders_domain(self):
        return [
            ('id', 'in', self._context.get('active_ids')),
            ('workcenter_id', '!=', False),
            ('state', '!=', 'done'),
        ]

    def _prepare_lines(self):
        lines = []
        if self.env.context.get('active_model') == "mrp.workorder":
            domain = self._workorders_domain()
            workorders = self.env['mrp.workorder'].search(domain)
            for wo in workorders.filtered(lambda x: x.main_product_id):
                lines.append((0, 0, {
                    'workorder_id': wo.id,
                    'product_id': wo.product_id.id,
                    'qty_producing': 1.,
                    'qty_production': wo.qty_production,
                    'qty_produced': wo.qty_produced,
                    'qty_nested': wo.qty_nested,
                }))
        return lines

    @api.model
    def default_get(self, values):
        res = super().default_get(values)
        domain = self._workorders_domain()
        workorders = self.env['mrp.workorder'].search(domain)
        products = self.env['product.product']
        for wo in workorders.filtered(lambda x: x.main_product_id):
            products |= wo.product_id
        if len(products) == 1:
            res.update({'product_id': products.id})
        res.update({'possible_product_ids': [(6, 0, products._ids)]})
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        delete_lines = [(2, i) for i in self.line_ids._ids]
        self.write({'line_ids': delete_lines})
        lines = self._prepare_lines()
        self.write({'line_ids': lines})
        if self.product_id:
            delete_lines = [(2, i) for i in self.line_ids.filtered(
                lambda x: x.product_id != self.product_id)._ids]
            self.write({'line_ids': delete_lines})

    def action_done(self):
        main_product_workcenter = {}
        for line in self.line_ids:
            wo = line.workorder_id
            if line.qty_producing + wo.qty_produced > wo.qty_production:
                raise exceptions.ValidationError(
                    _("the quantity to be produced must be less than or "
                      "equal to quantity produced"))
            workcenter_dict = main_product_workcenter.get(
                wo.main_product_id.id)
            if workcenter_dict:
                res_workorders = workcenter_dict.get(
                    wo.workcenter_id.id, self.env['mrp.workorder'])
                res_workorders |= line
                workcenter_dict.update({wo.workcenter_id.id: res_workorders})
            else:
                main_product_workcenter.update({wo.main_product_id.id: {
                    wo.workcenter_id.id: line}})
        for main_id, workcenters in main_product_workcenter.items():
            for workcenter, lines in workcenters.items():
                new_lines = [(0, 0, {'workorder_id': line.workorder_id.id,
                                     'qty_producing': line.qty_producing})
                             for line in lines]
                self.env['mrp.workorder.nest'].create({
                    'code': self.nest_code,
                    'main_product_id': main_id,
                    'workcenter_id': workcenter,
                    'nested_line_ids': new_lines,
                })


class NestedLinesInfo(models.TransientModel):
    _name = "nested.lines.info"

    nest_id = fields.Many2one(comodel_name="nested.new.line", string="Nest")
    workorder_id = fields.Many2one(comodel_name="mrp.workorder",
                                   string="Workorder")
    product_id = fields.Many2one(comodel_name='product.product')
    qty_producing = fields.Float(string="Currently Produced Quantity",
                                 default=1.)
    qty_production = fields.Float(string="Produce Quantity")
    qty_produced = fields.Float(string="Produce Quantity")
    qty_nested = fields.Float(string="Nested Quantity")
