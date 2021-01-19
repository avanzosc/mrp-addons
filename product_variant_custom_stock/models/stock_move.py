# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _has_parent(self, parent_location):
        if not self.location_id:
            return False
        elif self.location_id == parent_location:
            return True
        else:
            return self.location_id._has_parent(parent_location)


class StockMove(models.Model):
    _inherit = "stock.move"

    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Product Version",
                                         compute="_compute_product_version",
                                         store=True)
    manual_product_version_id = fields.Many2one(
        comodel_name="product.version", name="Manual Product Version")
    real_stock = fields.Float(string="Real In",
                              compute="_compute_move_in_out_qty", store=True)
    virtual_stock = fields.Float(string="Virtual In",
                                 compute="_compute_move_in_out_qty",
                                 store=True)

    def _calculate_qty_available(self, domain_move_in_loc,
                                 domain_move_out_loc):
        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [(
            'product_id', 'in', self.ids)] + domain_move_out_loc
        domain_move_in_todo = [('state', '=', 'done')] + domain_move_in
        domain_move_out_todo = [('state', '=', 'done')] + domain_move_out
        Move = self.env['stock.move']
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for
                            item in Move.read_group(
            domain_move_in_todo, ['product_id', 'product_qty'],
            ['product_id'], orderby='id'))
        moves_res = dict(
            (item['product_id'][0],
             moves_in_res[item['product_id'][0]] - item['product_qty'])
            for item in Move.read_group(
                domain_move_out_todo, ['product_id', 'product_qty'],
                ['product_id'], orderby='id'))
        return moves_res

    @api.depends("location_id", "location_dest_id", "product_qty",
                 "product_version_id.initial_stock_date", "state")
    def _compute_move_in_out_qty(self):
        location_obj = self.env['stock.location']
        physical_location = location_obj.search(
            [('name', '=', 'Physical Locations')])
#        virtual_location = location_obj.search(
#            [('name', '=', 'Virtual Locations')])
        for move in self:
            if move.product_version_id:
                if move.location_dest_id._has_parent(physical_location) and \
                        move.state == "done":
                    move.real_stock = move.product_qty
                    move.virtual_stock = 0
                elif move.location_id._has_parent(physical_location) and \
                        move.state == "done":
                    move.real_stock = -move.product_qty
                    move.virtual_stock = 0
                elif move.location_dest_id._has_parent(physical_location) \
                        and move.state in ('waiting', 'confirmed',
                                           'assigned', 'partially_available'):
                    move.virtual_stock = move.product_qty
                elif move.location_id._has_parent(physical_location) and \
                        move.state in ('waiting', 'confirmed', 'assigned',
                                       'partially_available'):
                    move.virtual_stock = -move.product_qty

    @api.depends('product_id')
    def _compute_product_version(self):
        for move in self:
            product_version = move.manual_product_version_id
            try:
                product_version = move.sale_line_id.product_version_id
            except AttributeError:
                pass
            try:
                product_version = \
                    product_version or \
                    move.purchase_line_id.product_version_id
            except AttributeError:
                pass
            try:
                product_version = product_version or \
                    move.raw_material_production_id.product_version_id
            except AttributeError:
                pass
            move.product_version_id = product_version
