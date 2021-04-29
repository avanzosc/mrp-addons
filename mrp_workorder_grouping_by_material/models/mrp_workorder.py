# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    main_product_id = fields.Many2one(comodel_name="product.product",
                                      string="Main Product",
                                      computed="_compute_main_product_id")
    nested_ids = fields.Many2many(comodel_name="mrp.workorder.nest",
                                  string="In Nests",
                                  compute="_compute_nested_ids")

    def _compute_nested_ids(self):
        for order in self:
            nest_ids = self.env['mrp.workorder.nest.line'].search([
                ('workorder_id', '=', order.id)]).mapped('nest_id')
            order.nested_ids = [(6, 0, nest_ids.ids)]

    def _check_final_product_lots(self):
        if (self.production_id.product_id.tracking != 'none') and not \
                self.final_lot_id and self.move_raw_ids:
            return False

    @api.depends("operation_id", "production_id")
    def _compute_main_product_id(self):
        for record in self:
            bom_id = record.production_id.bom_id
            main_product_bom_line = bom_id.bom_line_ids.filtered(
                lambda x: x.main_product_id)
            if main_product_bom_line.operation_id == record.operation_id:
                record.main_product_id = main_product_bom_line.product_id

    @api.multi
    def button_finish(self):
        for wo in self:
            if not wo.workcenter_id.nesting_required:
                return super(MrpWorkorder, wo).button_finish()

    @api.multi
    def button_start(self):
        for wo in self:
            if not wo.workcenter_id.nesting_required:
                return super(MrpWorkorder, wo).button_start()

    @api.multi
    def record_production(self):
        for wo in self:
            if not wo.workcenter_id.nesting_required:
                return super(MrpWorkorder, wo).record_production()

    @api.multi
    def button_pending(self):
        for wo in self:
            if not wo.workcenter_id.nesting_required:
                return super(MrpWorkorder, wo).button_pending()

    @api.multi
    def button_unblock(self):
        for wo in self:
            if not wo.workcenter_id.nesting_required:
                return super(MrpWorkorder, wo).button_unblock()

    @api.multi
    def button_scrap(self):
        for wo in self:
            if not wo.workcenter_id.nesting_required:
                return super(MrpWorkorder, wo).button_scrap()
