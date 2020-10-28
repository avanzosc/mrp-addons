# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.production.lot"

    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Product Version")
    version_value_ids = fields.One2many(
        comodel_name="product.version.line",
        related="product_version_id.custom_value_ids")
    custom_value_ids = fields.One2many(
        comodel_name="lot.version.custom.line", string="Custom Values",
        inverse_name="line_id", copy=True)

    def _set_custom_lines(self):
        if self.product_version_id:
            return self.product_version_id.get_custom_value_lines()
        elif self.product_id:
            return self.product_id.get_custom_value_lines()

    @api.onchange('product_id')
    def product_id_change(self):
        self.custom_value_ids = self._set_custom_lines()
        self.product_version_id = False

    @api.onchange('product_version_id')
    def product_version_id_change(self):
        if self.product_version_id:
            self.product_id = self.product_version_id.product_id
        else:
            self.custom_value_ids = self._set_custom_lines()

    # @api.model_create_multi
    # def create(self, vals_list):
    #     active_picking_id = self.env.context.get('active_picking_id', False)
    #     if active_picking_id:
    #         picking_id = self.env['stock.picking'].browse(active_picking_id)
    #         if picking_id and not picking_id.picking_type_id.use_create_lots:
    #             raise UserError(_('You are not allowed to create a lot or serial number with this operation type. To change this, go on the operation type and tick the box "Create New Lots/Serial Numbers".'))
    #     return super(ProductionLot, self).create(vals_list)


class LotVersionCustomLine(models.Model):
    _inherit = "version.custom.line"
    _name = "lot.version.custom.line"

    line_id = fields.Many2one(comodel_name="stock.production.lot")
