# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

from .mrp_workorder_nest import NEST_STATE

_logger = logging.getLogger(__name__)


class MrpWorkorderNestLine(models.Model):
    _name = "mrp.workorder.nest.line"
    _description = "Nested Lines"

    def _get_selection_workorder_state(self):
        return self.env["mrp.workorder"].fields_get(allfields=["state"])["state"][
            "selection"
        ]

    def default_workorder_state(self):
        default_dict = self.env["mrp.workorder"].default_get(["state"])
        return default_dict.get("state")

    def default_nest_state(self):
        default_dict = self.env["mrp.workorder.nest"].default_get(["state"])
        return default_dict.get("state")

    nest_id = fields.Many2one(
        string="Nested Work Orders",
        comodel_name="mrp.workorder.nest",
        required=True,
        ondelete="cascade",
    )
    qty_producing = fields.Float(
        string="Quantity Producing",
        default=1.0,
        digits="Product Unit of Measure",
        copy=True,
    )
    finished_lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot/Serial Number",
        domain="[('product_id', '=', product_id)]",
    )
    workorder_id = fields.Many2one(
        string="Workorder",
        comodel_name="mrp.workorder",
        required=True,
    )
    qty_produced = fields.Float(
        string="Quantity Produced", related="workorder_id.qty_produced"
    )
    qty_nested = fields.Float(
        string="Nested Quantity", related="workorder_id.qty_nested"
    )
    name = fields.Char(related="workorder_id.name", string="Name")
    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        related="workorder_id.workcenter_id",
        string="Workcenter",
        readonly=True,
    )
    main_product_id = fields.Many2one(
        comodel_name="product.product",
        related="workorder_id.main_product_id",
        string="Main Product",
        readonly=True,
    )
    date_planned_start = fields.Datetime(
        related="workorder_id.date_planned_start",
        string="Scheduled Date Start",
        readonly=True,
    )
    production_id = fields.Many2one(
        comodel_name="mrp.production",
        related="workorder_id.production_id",
        string="Production",
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="workorder_id.product_id",
        string="Product",
        readonly=True,
    )
    product_tracking = fields.Selection(related="product_id.tracking")
    qty_production = fields.Float(
        string="Original Production Quantity",
        related="workorder_id.qty_production",
        readonly=1,
    )
    qty_remaining = fields.Float(
        related="workorder_id.qty_remaining",
        string="Quantity To Be Produced",
        digits="Product Unit of Measure",
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="workorder_id.product_uom_id",
        string="Unit of Measure",
        readonly=True,
    )
    state = fields.Selection(
        string="Status",
        selection=NEST_STATE,
        default=default_nest_state,
    )
    workorder_state = fields.Selection(
        string="Workorder Status", related="workorder_id.state", readonly=True
    )
    working_state = fields.Selection(
        string="Workcenter Status", related="workorder_id.working_state", readonly=True
    )
    is_produced = fields.Boolean(related="workorder_id.is_produced")
    is_user_working = fields.Boolean(related="workorder_id.is_user_working")
    production_state = fields.Selection(
        related="workorder_id.production_state", readonly=1
    )
    company_id = fields.Many2one(related="workorder_id.company_id")
    ok_line = fields.Boolean(string="Ok")
    # possible_workorder_ids = fields.Many2many(
    #     comodel_name="mrp.workorder",
    #     compute="_compute_possible_workorder_ids",
    #     string="Possible Workorders",
    # )
    worksheet = fields.Binary(
        string="Worksheet", related="workorder_id.worksheet", readonly=True
    )

    @api.depends(
        "nest_id",
        "nest_id.main_product_id",
        "nest_id.workcenter_id",
        "nest_id.workorder_ids",
    )
    def _compute_possible_workorder_ids(self):
        workorder_obj = self.env["mrp.workorder"]
        for nest_line in self:
            nest = nest_line.nest_id
            assigned_wo = nest.workorder_ids.ids
            workorders = workorder_obj.search(
                [
                    ("main_product_id", "=", nest.main_product_id.id),
                    ("workcenter_id", "=", nest.workcenter_id.id),
                    ("id", "not in", assigned_wo),
                    ("state", "not in", ["done", "cancel"]),
                ]
            )
            nest_line.possible_workorder_ids = [(6, 0, workorders.ids or [])]

    @api.depends("production_id.product_qty", "qty_produced")
    def _compute_is_produced(self):
        self.is_produced = False
        for line in self.filtered(lambda p: p.workorder_id.production_id):
            rounding = line.workorder_id.production_id.product_uom_id.rounding
            production_qty = line.workorder_id._get_real_uom_qty(line.qty_producing)
            line.is_produced = (
                float_compare(
                    line.finished_qty, production_qty, precision_rounding=rounding
                )
                >= 0
            )

    def open_workorder_view(self):
        self.ensure_one()
        return self.workorder_id.action_open_wizard()
        # view_id = self.env["ir.model.data"]._xmlid_to_res_id(
        #     "mrp.mrp_production_workorder_form_view_inherit"
        # )
        # return {
        #     "name": _("Workorder"),
        #     "domain": [],
        #     "res_model": "mrp.workorder",
        #     "res_id": self.workorder_id.id,
        #     "type": "ir.actions.act_window",
        #     "view_mode": "form",
        #     "view_type": "form",
        #     "view_id": view_id,
        #     "context": {},
        #     "target": "current",
        # }

    def _get_line(self, direction):
        self.ensure_one()
        index_change = 0
        if direction == "next":
            index_change = 1
        elif direction == "previous":
            index_change = -1
        nest_lines = self.nest_id.nested_line_ids
        line_index = -1
        for index, line in enumerate(nest_lines):
            if self.id == line.id:
                line_index = index + index_change
        res_id = nest_lines[line_index].id if line_index >= 0 else self.id
        return res_id

    def button_get_previous_line(self):
        self.ensure_one()
        res_id = self._get_line(direction="previous")
        return self.nest_line_form_view(res_id)

    def button_get_next_line(self):
        self.ensure_one()
        res_id = self._get_line(direction="next")
        return self.nest_line_form_view(res_id)

    def get_worksheets(self):
        lines = self.filtered("workorder_id.worksheet")
        return lines.mapped("workorder_id.worksheet")

    def show_worksheets(self):
        worksheets = self.get_worksheets()
        if not worksheets:
            return
        wizard = self.env["binary.container"].create(
            {
                "binary_field": (
                    worksheets[0] if isinstance(worksheets, list) else worksheets
                ),
            }
        )
        action = self.env.ref("pdf_previewer.binary_container_action")
        action_dict = action and action.read()[0] or {}
        action_dict.update(
            {
                "name": _("Worksheet"),
                "res_id": wizard.id,
            }
        )
        return action_dict

    def _create_assign_lot(self, code, product_id):
        lot_obj = self.env["stock.lot"]
        lot_id = False
        if code:
            if product_id.tracking == "lot":
                lot_id = lot_obj.search(
                    [
                        ("name", "=", code),
                        ("company_id", "=", self.env.company.id),
                        ("product_id", "=", product_id.id),
                    ],
                    limit=1,
                ).id
            else:
                return False
            if not lot_id:
                return lot_obj.create(
                    {
                        "name": code,
                        "product_id": product_id.id,
                        "company_id": self.env.company.id,
                    }
                ).id
        return lot_id

    @api.model
    def create(self, vals):
        workorder = self.env["mrp.workorder"].browse(vals.get("workorder_id"))
        product = workorder.product_id
        code = workorder.production_id.name
        vals["finished_lot_id"] = self._create_assign_lot(code, product)
        return super().create(vals)

    def _write_lot_producing_qty(self):
        for n_line in self:
            wo = n_line.workorder_id
            if wo.state not in ("done", "cancel"):
                res = {
                    "qty_producing": n_line.qty_producing,
                }
                # line_values = wo._update_workorder_lines()
                # wo.update_workorder_lines(line_values)
                if n_line.finished_lot_id:
                    res.update(
                        {
                            "finished_lot_id": n_line.finished_lot_id.id,
                        }
                    )
                if res:
                    wo.write(res)
                    # wo._apply_update_workorder_lines()
                if n_line.nest_id.lot_id:
                    workorder_lines = n_line.workorder_id.move_raw_ids.move_line_ids
                    move_lines = workorder_lines.filtered(
                        lambda x: x.product_id == n_line.nest_id.main_product_id
                    )
                    for move_line in move_lines:
                        move_line.write(
                            {
                                "lot_id": n_line.nest_id.lot_id.id,
                                "qty_done": move_line.reserved_qty,
                            }
                        )
                # if res:
                #     n_line.workorder_id.write(res)

    def button_finish(self):
        for nl in self.filtered(
            lambda n: n.is_produced and n.workorder_state == "progress"
        ):
            nl.workorder_id.with_context(from_nest=True).button_finish()

    def _check_final_product_lot(self):
        for wo in self.mapped("workorder_id"):
            if not wo._check_final_product_lots():
                raise UserError(
                    _(
                        "{}: You should provide a lot/serial number for the "
                        "final product."
                    ).format(wo.display_name)
                )

    def action_back2draft(self):
        for nl in self.filtered(lambda n: n.state == "ready"):
            nl.state = "draft"

    def action_check_ready(self):
        for nl in self.filtered(lambda n: n.state == "draft"):
            if nl.workorder_id.state in ("ready", "progress"):
                nl.state = "ready"
            elif nl.workorder_id.state == "done":
                nl.state = "done"

    # def action_cancel(self):
    #     if not any(self.filtered(lambda n: n.state == "ready")):
    #         raise UserError(_(""))
    #     return self.write({"state": "cancel"})

    def button_start(self):
        for nl in self.filtered(lambda n: n.state == "ready"):
            nl._write_lot_producing_qty()
            nl._check_final_product_lot()
            nl.workorder_id.with_context(from_nest=True).button_start()
            nl.state = "progress"

    def record_production(self):
        for nl in self.filtered(lambda n: n.state == "progress"):
            wo = nl.workorder_id
            if wo.state == "progress" and not wo.is_produced:
                nl._write_lot_producing_qty()
                nl._check_final_product_lot()
                try:
                    if wo.current_quality_check_id.quality_state == "none":
                        wo.current_quality_check_id.do_pass()
                except AttributeError:
                    # If enterprise module mrp_workorder is not installed
                    # quality check is not necessary
                    _logger.info("Enterprise module 'mrp_workorder' is not installed")
                try:
                    wo.with_context(from_nest=True).record_production()
                    nl.state = "done"
                except UserError as exc:
                    raise UserError(
                        _("%(workorder)s: %(error_name)s")
                        % {
                            "workorder": wo.name,
                            "error_name": str(exc.name),
                        }
                    ) from exc

    def button_pending(self):
        for nl in self:
            is_user_working = nl.workorder_id.is_user_working
            if (
                nl.working_state != "blocked"
                and is_user_working
                and nl.workorder_id.state not in ("done", "pending", "ready", "cancel")
            ):
                nl.workorder_id.with_context(from_nest=True).button_pending()

    def button_scrap(self):
        for nest_line in self.filtered(
            lambda nl: nl.workorder_state not in ("confirmed", "cancel")
        ):
            nest_line.workorder_id.with_context(from_nest=True).button_scrap()

    def button_quality_alert(self):
        return self.workorder_id.button_quality_alert()

    def button_unblock(self):
        return self.workcenter_id.unblock()

    def button_change_ok_line(self):
        self.ok_line = not self.ok_line
        return self.nest_line_form_view(self.id)
