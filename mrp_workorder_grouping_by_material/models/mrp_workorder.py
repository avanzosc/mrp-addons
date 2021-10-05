# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    main_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Main Product",
        compute="_compute_main_product_id",
        store=True)
    nested_ids = fields.Many2many(
        comodel_name="mrp.workorder.nest",
        string="In Nests",
        compute="_compute_nested")
    qty_nested = fields.Float(
        string="Nested Quantity",
        compute="_compute_nested")
    nesting_required = fields.Boolean(
        string="Nesting Required",
        related="workcenter_id.nesting_required",
        store=True)

    def _compute_nested(self):
        for order in self:
            nest_ids = self.env["mrp.workorder.nest.line"].search([
                ("workorder_id", "=", order.id)]).mapped("nest_id")
            order.nested_ids = [(6, 0, nest_ids.ids)]
            order.qty_nested = sum(nest_ids.mapped("qty_producing"))

    def _link_to_quality_check(self, old_move_line, new_move_line):
        return True

    def _check_final_product_lots(self):
        self.ensure_one()
        if ((self.production_id.product_id.tracking != 'none') and
                not self.finished_lot_id and self.move_raw_ids):
            return False

    @api.depends("operation_id", "production_id", "production_id.bom_id",
                 "production_id.bom_id.bom_line_ids",
                 "production_id.bom_id.bom_line_ids.product_id",
                 "production_id.bom_id.bom_line_ids.main_material")
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
        self.ensure_one()
        from_nest = self.env.context.get("from_nest")
        if not from_nest and self.workcenter_id.nesting_required:
            raise exceptions.UserError(
                _("The workcenter is 'nesting_required'"))
        return super().button_finish()

    def button_start(self):
        self.ensure_one()
        from_nest = self.env.context.get("from_nest")
        if not from_nest and self.workcenter_id.nesting_required:
            raise exceptions.UserError(
                _("The workcenter is 'nesting_required'"))
        return super().button_start()

    def record_production(self):
        self.ensure_one()
        from_nest = self.env.context.get("from_nest")
        if not from_nest and self.workcenter_id.nesting_required:
            raise exceptions.UserError(
                _("The workcenter is 'nesting_required'"))
        return super().record_production()

    def button_pending(self):
        from_nest = self.env.context.get("from_nest")
        if not from_nest and any(self.filtered(
                "workcenter_id.nesting_required")):
            raise exceptions.UserError(
                _("The workcenter is 'nesting_required'"))
        return super().button_pending()

    def button_unblock(self):
        from_nest = self.env.context.get("from_nest")
        if not from_nest and any(self.filtered(
                "workcenter_id.nesting_required")):
            raise exceptions.UserError(
                _("The workcenter is 'nesting_required'"))
        return super().button_unblock()

    def button_scrap(self):
        self.ensure_one()
        from_nest = self.env.context.get("from_nest")
        if not from_nest and self.workcenter_id.nesting_required:
            raise exceptions.UserError(
                _("The workcenter is 'nesting_required'"))
        return super().button_scrap()
