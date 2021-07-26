# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    main_product_id = fields.Many2one(comodel_name="product.product",
                                      string="Main Product",
                                      compute="_compute_main_product_id",
                                      store=True)
    nested_ids = fields.Many2many(comodel_name="mrp.workorder.nest",
                                  string="In Nests",
                                  compute="_compute_nested_ids")
    qty_nested = fields.Float(string="Nested Quantity",
                              compute="_compute_qty_nested")

    @api.depends('nested_ids')
    def _compute_qty_nested(self):
        self.qty_nested = sum(self.nested_ids.mapped("qty_producing"))

    def _link_to_quality_check(self, old_move_line, new_move_line):
        return True

    def _compute_nested_ids(self):
        for order in self:
            nest_ids = self.env['mrp.workorder.nest.line'].search([
                ('workorder_id', '=', order.id)]).mapped('nest_id')
            order.nested_ids = [(6, 0, nest_ids.ids)]

    def _check_final_product_lots(self):
        if (self.production_id.product_id.tracking != 'none') and not \
                self.finished_lot_id and self.move_raw_ids:
            return False

    @api.depends("operation_id", "production_id")
    def _compute_main_product_id(self):
        for record in self:
            bom_id = record.production_id.bom_id
            main_product_bom_line = bom_id.bom_line_ids.filtered(
                lambda x: x.operation_id == record.operation_id and
                x.main_material)
            if main_product_bom_line:
                record.main_product_id = main_product_bom_line.product_id
            else:
                record.main_product_id = False

    def button_finish(self):
        from_nest = self.env.context.get('from_nest')
        for wo in self:
            if not from_nest and wo.workcenter_id.nesting_required:
                raise exceptions.UserError("The workcenter is "
                                           "'nesting_required'")
            return super(MrpWorkorder, wo).button_finish()

    def button_start(self):
        from_nest = self.env.context.get('from_nest')
        for wo in self:
            if not from_nest and wo.workcenter_id.nesting_required:
                raise exceptions.UserError("The workcenter is "
                                           "'nesting_required'")
            return super(MrpWorkorder, wo).button_start()

    def record_production(self):
        from_nest = self.env.context.get('from_nest')
        for wo in self:
            if not from_nest and wo.workcenter_id.nesting_required:
                raise exceptions.UserError("The workcenter is "
                                           "'nesting_required'")
            return super(MrpWorkorder, wo).record_production()

    def button_pending(self):
        from_nest = self.env.context.get('from_nest')
        for wo in self:
            if not from_nest and wo.workcenter_id.nesting_required:
                raise exceptions.UserError("The workcenter is "
                                           "'nesting_required'")
            return super(MrpWorkorder, wo).button_pending()

    def button_unblock(self):
        from_nest = self.env.context.get('from_nest')
        for wo in self:
            if not from_nest and wo.workcenter_id.nesting_required:
                raise exceptions.UserError("The workcenter is "
                                           "'nesting_required'")
            return super(MrpWorkorder, wo).button_unblock()

    def button_scrap(self):
        from_nest = self.env.context.get('from_nest')
        for wo in self:
            if not from_nest and wo.workcenter_id.nesting_required:
                raise exceptions.UserError("The workcenter is "
                                           "'nesting_required'")
            return super(MrpWorkorder, wo).button_scrap()
