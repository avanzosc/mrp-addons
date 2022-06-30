# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import tempfile

from PyPDF2 import PdfFileMerger

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.models import expression
from odoo.tools import safe_eval

NEST_STATE = [
    ("draft", "Draft"),
    ("ready", "Ready"),
    ("progress", "In Progress"),
    ("blocked", "Blocked"),
    ("done", "Done"),
    ("cancel", "Cancelled"),
]


class MrpWorkorderNest(models.Model):
    _name = "mrp.workorder.nest"
    _description = "Nested Work Orders"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", readonly=True, required=True,
                       copy=False, default="New")
    code = fields.Char(string="Code")
    main_product_id = fields.Many2one(comodel_name="product.product")
    possible_main_product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_possible_main_products")
    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter")
    workorder_ids = fields.Many2many(
        comodel_name="mrp.workorder",
        compute="_compute_workorders",
        store=True)
    possible_workcenter_ids = fields.Many2many(
        comodel_name="mrp.workcenter",
        compute="_compute_possible_workcenter")
    main_product_tracking = fields.Selection(
        related="main_product_id.tracking")
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True)
    nested_line_ids = fields.One2many(
        comodel_name="mrp.workorder.nest.line",
        inverse_name="nest_id",
        string="Nested Lines",
        copy=True)
    state = fields.Selection(
        selection=NEST_STATE,
        string="State",
        default="draft",
        tracking=True)
    pre_block_state = fields.Selection(
        selection=NEST_STATE, string="Pre Block State")
    line_state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("ready", "Ready"),
            ("progress", "Progress"),
            ("blocked", "Blocked"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ], compute="_compute_line_states")
    line_working_state = fields.Selection(
        string="Workcenter Status",
        related="workcenter_id.working_state",
        readonly=False,
        help="Technical: used in views only")
    line_production_state = fields.Selection(
        selection=[
            ("undone", "Undone"),
            ("done", "Done"),
        ], compute="_compute_line_states")
    line_is_produced = fields.Boolean(compute="_compute_line_states")
    line_is_user_working = fields.Boolean(compute="_compute_line_states")
    worksheets = fields.Binary(string="PDF", help="Upload your PDF file.")
    qty_producing = fields.Float(
        string="Quantity Producing",
        compute="_compute_qty_producing",
        digits="Product Unit of Measure")
    done_cancel_lines = fields.Boolean(
        string="No Active Lines",
        compute="_compute_active_lines",
        store=True)
    date_planned_start = fields.Datetime(
        compute="_compute_date_planned_start",
        string="Scheduled Date Start",
        store=True)
    show_worksheet = fields.Boolean(
        compute="_compute_show_worksheet")

    @api.depends("nested_line_ids", "nested_line_ids.date_planned_start")
    def _compute_date_planned_start(self):
        for nest in self:
            dates = list(filter(lambda x: x, nest.mapped(
                "nested_line_ids.date_planned_start")))
            if dates:
                nest.date_planned_start = min(filter(lambda x: x, dates))

    @api.depends("nested_line_ids.qty_producing")
    def _compute_qty_producing(self):
        for nest in self:
            nest.qty_producing = sum(nest.nested_line_ids.filtered(
                lambda x: x.state == "progress").mapped("qty_producing"))

    def _compute_possible_main_products(self):
        product_ids = self.env["mrp.bom.line"].search(
            [("main_material", "=", True)]).mapped("product_id").ids
        for nest in self:
            nest.possible_main_product_ids = [(6, 0, product_ids or [])]

    def _compute_possible_workcenter(self):
        workcenter_ids = self.env["mrp.workcenter"].search(
            [("nesting_required", "=", True)]).ids
        for nest in self:
            nest.possible_workcenter_ids = [(6, 0, workcenter_ids or [])]

    @api.depends("nested_line_ids", "nested_line_ids.workorder_id")
    def _compute_workorders(self):
        for nest in self:
            assigned_wo = nest.mapped("nested_line_ids.workorder_id").ids
            nest.workorder_ids = [(6, 0, assigned_wo)]

    def _compute_show_worksheet(self):
        for nest in self:
            nest.show_worksheet = any(
                nest.mapped("nested_line_ids.workorder_id.worksheet"))

    def name_get(self):
        result = []
        for record in self:
            name = "{}{}{}".format(record.name or "",
                                   record.code and "/" or "",
                                   record.code or "")
            result.append((record.id, name))
        return result

    # @api.onchange("lot_id")
    # def onchange_lot_id(self):
    #     for line in self.nested_line_ids:
    #         line.lot_id = self.lot_id.id

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "mrp.workorder.nest") or "New"
        result = super().create(vals)
        return result

    def _check_lot(self):
        self.ensure_one()
        if not bool(self.main_product_id.tracking == "none" or self.lot_id):
            raise UserError(_("Main product lot is not selected"))

    def action_check_ready(self):
        for nest in self.filtered(lambda n: n.state == "draft"):
            nest.nested_line_ids.action_check_ready()
            if not any(nest.nested_line_ids.filtered(
                    lambda l: l.state not in ("ready", "progress"))):
                nest.state = "ready"

    def nest_start(self):
        for nest in self.filtered(lambda n: n.state == "ready"):
            nest._check_lot()
            nest.state = "progress"

    def nest_draft(self):
        for nest in self.filtered(lambda n: n.state == "ready"):
            nest.nested_line_ids.action_back2draft()
            nest.state = "draft"

    def nest_blocked(self):
        for nest in self:
            if nest.state != "blocked":
                nest.pre_block_state = nest.state
                nest.state = "blocked"

    def nest_unblocked(self):
        for nest in self:
            if nest.state == "blocked":
                nest.state = nest.pre_block_state
                if nest.line_working_state == "blocked":
                    nest.button_unblock()

    def button_finish(self):
        for nest in self:
            nest.nested_line_ids.button_finish()

    def button_start(self):
        self.action_check_ready()
        for nest in self:
            nest.nest_start()
            nest.nested_line_ids.button_start()
            # nest.state = "progress"

    def record_production(self):
        for nest in self:
            nest._check_lot()
            nest.nested_line_ids.record_production()
            nest.nest_blocked()

    def button_pending(self):
        for nest in self:
            nest.nested_line_ids.button_pending()

    def button_unblock(self):
        for nest in self:
            nest.workcenter_id.unblock()

    def button_scrap(self):
        for nest in self:
            nest.nested_line_ids.button_scrap()

    # def check_status(self):
    #     for nest in self:
    #         if not any(nest.nested_line_ids.filtered(
    #                 lambda l: l.state == "done" and l.workorder_state == "done")):
    #             nest.state == "done"

    @api.depends("nested_line_ids")
    def _compute_active_lines(self):
        for nest in self:
            for wl in nest.nested_line_ids:
                if wl.workorder_id.state in ["done", "cancel"]:
                    nest.done_cancel_lines = True
                else:
                    nest.done_cancel_lines = False

    @api.depends("nested_line_ids", "workcenter_id")
    def _compute_line_states(self):
        for nest in self:
            state = "done"
            production_state = "done"
            is_produced = True
            is_user_working = True
            for wl in nest.nested_line_ids:
                if wl.state != "done":
                    state = wl.state
                if wl.production_state != "done":
                    production_state = "undone"
                if not wl.workorder_id.is_produced:
                    is_produced = False
                if not wl.workorder_id.is_user_working:
                    is_user_working = False

            if nest.line_working_state == "blocked" and \
                    nest.state not in ["done", "blocked"]:
                nest.pre_block_state = nest.state
                nest.state = "blocked"
            nest.line_state = state
            nest.line_production_state = production_state
            nest.line_is_user_working = is_user_working
            nest.line_is_produced = is_produced

    def get_worksheets(self):
        worksheets = self.mapped("nested_line_ids").get_worksheets()
        if not worksheets:
            return
        merger = PdfFileMerger(strict=False)
        for worksheet in worksheets:
            temp = tempfile.NamedTemporaryFile(suffix=".pdf")
            with open(temp.name, "wb") as temp_pdf:
                pdf = base64.b64decode(worksheet)
                temp_pdf.write(pdf)
            merger.append(temp.name, import_bookmarks=False)
        temp = tempfile.NamedTemporaryFile(suffix=".pdf")
        merger.write(temp.name)
        merger.close()
        with open(temp.name, "rb") as merged_pdf:
            content_merged_pdf = merged_pdf.read()
        return base64.b64encode(content_merged_pdf)

    def show_worksheets(self):
        binary = self.get_worksheets()
        if not binary:
            return
        wizard = self.env["binary.container"].create({
            "binary_field": binary,
        })
        action = self.env.ref("pdf_previewer.binary_container_action")
        action_dict = action and action.read()[0] or {}
        action_dict.update({
            "name": _("Worksheets"),
            "res_id": wizard.id,
        })
        return action_dict

    def show_nested_lines(self):
        action = self.env.ref(
            "mrp_workorder_grouping_by_material.mrp_workorder_nest_line_action")
        action_dict = action and action.read()[0] or {}
        domain = expression.AND([
            [("nest_id", "in", self.ids)], safe_eval(action.domain or "[]")])
        action_dict.update({
            "domain": domain,
            "limit": 10,
        })
        return action_dict
