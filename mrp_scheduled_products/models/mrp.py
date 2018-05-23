# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp


class MrpProductionProductLine(models.Model):
    _name = 'mrp.production.product.line'
    _description = 'Production Scheduled Product'

    name = fields.Char(string='Name', required=True)
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product', required=True)
    product_qty = fields.Float(string='Product Quantity',
                               digits=dp.get_precision(
                                   'Product Unit of Measure'), required=True)
    product_uom = fields.Many2one(comodel_name='product.uom',
                                  string='Product Unit of Measure',
                                  required=True)
    # product_uos_qty = fields.Float('Product UOS Quantity')
    # product_uos = fields.Many2one(comodel_name='product.uom',
    #                               string='Product UOS')
    production_id = fields.Many2one(comodel_name='mrp.production',
                                    string='Production Order')
    bom_line_id = fields.Many2one(comodel_name='mrp.bom.line', string='Bom '
                                                                      'Line')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_lines = fields.One2many(
        comodel_name='mrp.production.product.line',
        inverse_name='production_id', string='Scheduled goods')
    state = fields.Selection(selection_add=[('draft', 'Draft')],
                             default='draft')

    @api.multi
    def button_confirm(self):
        orders_to_confirm = self.filtered(lambda order: order.state == 'draft')
        return orders_to_confirm.write({'state': 'confirmed'})


    @api.multi
    def _generate_moves(self):
        """Avoid draft moves generation of draft state mo"""
        return super(MrpProduction, self.filtered(lambda x: x.state != "draft")
            )._generate_moves()

    @api.multi
    def button_confirm(self):
        self.write({'state': 'confirmed'})
        return self._generate_moves()

    @api.multi
    def _action_compute_lines(self):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """
        # if properties is None:
        #     properties = []
        results = []
        prod_line_obj = self.env['mrp.production.product.line']
        #workcenter_line_obj = self.env['mrp.production.workcenter.line']
        for production in self:
            #unlink product_lines
            production.product_lines.sudo().unlink()
            #unlink workcenter_lines
            # workcenter_line_obj.sudo().unlink(
            #     [line.id for line in production.workcenter_lines])

            res = production._prepare_lines()
            results = res # product_lines
            #results2 = res[1] # workcenter_lines

            # reset product_lines in production order
            for line in results:
                line_data = line[1]
                bom_line = line[0]
                product = bom_line.product_id
                prod_line = {
                    'name': product.name or bom_line.product_tmpl_id.name,
                    'product_id': product.id,
                    'product_qty': line_data['qty'],
                    'bom_line_id': bom_line.id,
                    'product_uom': bom_line.product_uom_id.id,
                    'production_id': production.id,
                }
                prod_line_obj.create(prod_line)

            #reset workcenter_lines in production order
            # for line in results2:
            #     line['production_id'] = production.id
            #     #workcenter_line_obj.create(line)
        return results

    @api.multi
    def _prepare_lines(self):
        # search BoM structure and route
        bom_obj = self.env['mrp.bom']
        uom_obj = self.env['product.uom']
        bom_point = self.bom_id
        bom_id = self.bom_id.id
        if not bom_point:
            bom_id = bom_obj._bom_find(product=self.product_id)
            if bom_id:
                bom_point = bom_obj.browse(bom_id)
                routing_id = bom_point.routing_id.id or False
                self.write({'bom_id': bom_id, 'routing_id': routing_id})

        if not bom_id:
            raise exceptions.except_orm(_('Error!'), _("Cannot find a bill of "
                                              "material for this product."))

        # get components and workcenter_lines from BoM structure
        factor = self.product_uom_id._compute_quantity(
            self.product_qty, bom_point.product_uom_id)
        # product_lines, workcenter_lines
        # return self.bom_id._bom_explode(
        #     cr, uid, bom_point, production.product_id,
        #     factor / bom_point.product_qty, properties,
        #     routing_id=production.routing_id.id, context=context)
        boms_done, lines_done = bom_point.explode(self.product_id, factor /
                                     bom_point.product_qty)
        return lines_done

    @api.multi
    def action_compute(self):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        return len(self._action_compute_lines())
