# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    main_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Main Product",
        compute="_compute_main_product_id",
        store=True,
    )
    nested_line_ids = fields.One2many(
        comodel_name="mrp.workorder.nest.line",
        string="Nest Lines",
        inverse_name="workorder_id",
    )
    nested_ids = fields.Many2many(
        comodel_name="mrp.workorder.nest",
        string="In Nests",
        compute="_compute_nested_ids",
        compute_sudo=True,
        store=True,
    )
    nested_count = fields.Integer(
        compute="_compute_nested_ids",
        compute_sudo=True,
    )
    qty_nested = fields.Float(
        string="Nested Quantity",
        compute="_compute_nested",
        compute_sudo=True,
    )
    nested_status = fields.Selection(
        selection=[
            ("less", "Nested Less Quantity"),
            ("equal", "Nested All Quantity"),
            ("plus", "Nested More Quantity"),
            ("not_nest", "Not Nested"),
        ],
        string="Nested Status",
        compute="_compute_nested",
        compute_sudo=True,
        store=True,
        default="not_nest",
    )
    nesting_required = fields.Boolean(
        string="Nesting Required", related="workcenter_id.nesting_required", store=True
    )

    @api.depends(
        "nested_line_ids",
        "nested_line_ids.nest_id",
    )
    def _compute_nested_ids(self):
        for order in self:
            order.nested_ids = [(6, 0, order.mapped("nested_line_ids.nest_id").ids)]
            order.nested_count = len(order.mapped("nested_line_ids.nest_id"))

    @api.depends(
        "nested_line_ids",
        "nested_line_ids.qty_producing",
        "qty_production",
        "workcenter_id",
        "workcenter_id.nesting_required",
    )
    def _compute_nested(self):
        for order in self:
            qty_nested = sum(order.mapped("nested_line_ids.qty_producing"))
            if order.nested_line_ids or order.workcenter_id.nesting_required:
                if qty_nested > order.qty_production:
                    status = "plus"
                elif qty_nested < order.qty_production:
                    status = "less"
                else:
                    status = "equal"
            else:
                status = "not_nest"
            order.qty_nested = qty_nested
            order.nested_status = status

    def _link_to_quality_check(self, old_move_line, new_move_line):
        return True

    def _check_final_product_lots(self):
        self.ensure_one()
        if self.product_id.tracking != "none" and not self.finished_lot_id:
            return False
        return True

    @api.depends(
        "operation_id",
        "production_id",
        "production_id.bom_id",
        "production_id.bom_id.bom_line_ids",
        "production_id.bom_id.bom_line_ids.product_id",
        "production_id.bom_id.bom_line_ids.main_material",
    )
    def _compute_main_product_id(self):
        for record in self:
            bom_id = record.production_id.bom_id
            main_product_bom_line = bom_id.bom_line_ids.filtered(
                lambda x: x.operation_id == record.operation_id and x.main_material
            )
            record.main_product_id = (
                main_product_bom_line.product_id if main_product_bom_line else False
            )

    def ensure_nesting_required(self, from_nest=False):
        if not from_nest and any(self.mapped("workcenter_id.nesting_required")):
            raise exceptions.UserError(_("The workcenter is 'nesting_required'"))

    def button_finish(self):
        self.ensure_nesting_required(from_nest=self.env.context.get("from_nest"))
        return super().button_finish()

    def button_start(self):
        self.ensure_one()
        self.ensure_nesting_required(from_nest=self.env.context.get("from_nest"))
        return super().button_start()

    def record_production(self):
        self.ensure_one()
        self.ensure_nesting_required(from_nest=self.env.context.get("from_nest"))
        return super().record_production()

    def post_inventory(self):
        self.ensure_nesting_required(from_nest=self.env.context.get("from_nest"))
        return super().post_inventory()

    def button_pending(self):
        self.ensure_nesting_required(from_nest=self.env.context.get("from_nest"))
        return super().button_pending()

    def button_unblock(self):
        self.ensure_nesting_required(from_nest=self.env.context.get("from_nest"))
        return super().button_unblock()

    def button_scrap(self):
        self.ensure_one()
        self.ensure_nesting_required(from_nest=self.env.context.get("from_nest"))
        return super().button_scrap()

    def open_nest(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_workorder_grouping_by_material.mrp_workorder_nest_action"
        )
        action["domain"] = expression.AND(
            [
                [("id", "in", self.nested_ids.ids)],
                safe_eval(action.get("domain") or "[]"),
            ]
        )
        return action
