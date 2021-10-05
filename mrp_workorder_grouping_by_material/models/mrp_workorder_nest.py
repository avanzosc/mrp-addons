# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import tempfile

from PyPDF2 import PdfFileMerger

from odoo import api, fields, models, _
from odoo.exceptions import UserError

NEST_STATE = [
    ("draft", "Draft"),
    ("ready", "Ready"),
    ("progress", "In Progress"),
    ("blocked", "Blocked"),
    ("done", "Done"),
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
    workcenter_id = fields.Many2one(comodel_name="mrp.workcenter")
    workorder_ids = fields.Many2many(
        comodel_name="mrp.workorder",
        compute="_compute_workorders", store=True)
    possible_workcenter_ids = fields.Many2many(
        comodel_name="mrp.workcenter", compute="_compute_possible_workcenter")
    main_product_tracking = fields.Selection(
        related="main_product_id.tracking")
    lot_id = fields.Many2one(comodel_name="stock.production.lot")
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

    @api.depends("nested_line_ids")
    def _compute_workorders(self):
        for nest in self:
            assigned_wo = nest.mapped("nested_line_ids.workorder_id").ids
            nest.workorder_ids = [(6, 0, assigned_wo)]

    def name_get(self):
        result = []
        for record in self:
            name = "{}{}{}".format(record.name or "",
                                   record.code and "/" or "",
                                   record.code or "")
            result.append((record.id, name))
        return result

    @api.onchange("lot_id")
    def onchange_lot_id(self):
        for line in self.nested_line_ids:
            line.lot_id = self.lot_id.id

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "mrp.workorder.nest") or "New"
        result = super().create(vals)
        return result

    def nest_start(self):
        for nest in self:
            set_lot = bool(nest.main_product_id.tracking == "none" or
                           nest.lot_id)
            if nest.state == "draft" and set_lot:
                nest.state = "ready"
            else:
                raise UserError(_("Main product lot is not selected"))

    def nest_draft(self):
        for nest in self.filtered(lambda n: n.state == "ready"):
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
        for nest in self:
            nest_lines = nest.nested_line_ids
            nest_lines._check_final_product_lot()
            nest_lines.button_start()
            nest.state = "progress"

    def record_production(self):
        for nest in self:
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
        self.ensure_one()
        worksheets = self.mapped("nested_line_ids.workorder_id.worksheet")
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
        self.ensure_one()
        wizard = self.env["binary.container"].create({
            "binary_field": self.get_worksheets(),
        })
        action = self.env.ref("pdf_previewer.binary_container_action")
        action_dict = action and action.read()[0] or {}
        action_dict.update({
            "name": _("Worksheets"),
            "res_id": wizard.id,
        })
        return action_dict


class MrpWorkorderNestLine(models.Model):
    _name = "mrp.workorder.nest.line"

    def _get_selection_workorder_state(self):
        return self.env["mrp.workorder"].fields_get(
            allfields=["state"])["state"]["selection"]

    nest_id = fields.Many2one(
        comodel_name="mrp.workorder.nest",
        required=True)
    related_qty_producing = fields.Float(
        related="workorder_id.qty_producing")
    related_finished_lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        related="workorder_id.finished_lot_id")
    qty_producing = fields.Float(
        string="Quantity Producing", default=1.0,
        digits="Product Unit of Measure", copy=True)
    finished_lot_id = fields.Many2one(
        comodel_name="stock.production.lot", string="Lot/Serial Number",
        domain="[('product_id', '=', product_id)]")
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        domain="[('product_id', '=', nest_id.main_product_id.id)]")
    workorder_id = fields.Many2one(
        comodel_name="mrp.workorder")
    qty_produced = fields.Float(
        string="Quantity Produced",
        related="workorder_id.qty_produced")
    qty_nested = fields.Float(
        string="Nested Quantity",
        related="workorder_id.qty_nested")
    name = fields.Char(related="workorder_id.name", string="Name")
    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        related="workorder_id.workcenter_id",
        string="Workcenter",
        readonly=True)
    date_planned_start = fields.Datetime(
        related="workorder_id.date_planned_start",
        string="Scheduled Date Start",
        readonly=True)
    production_id = fields.Many2one(
        comodel_name="mrp.production",
        related="workorder_id.production_id",
        string="Production",
        readonly=1)
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="workorder_id.product_id",
        string="Product",
        readonly=1)
    product_tracking = fields.Selection(related="product_id.tracking")
    qty_production = fields.Float(
        string="Original Production Quantity",
        related="workorder_id.qty_production",
        readonly=1)
    qty_remaining = fields.Float(
        related="workorder_id.qty_remaining",
        string="Quantity To Be Produced",
        digits="Product Unit of Measure")
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="workorder_id.product_uom_id",
        string="Unit of Measure",
        readonly=1)
    state = fields.Selection(
        string="State",
        related="workorder_id.state",
        selection=_get_selection_workorder_state,
        readonly=True)
    working_state = fields.Selection(
        string="Workcenter Status",
        related="workorder_id.working_state",
        readonly=True)
    is_produced = fields.Boolean(related="workorder_id.is_produced")
    is_user_working = fields.Boolean(related="workorder_id.is_user_working")
    production_state = fields.Selection(
        related="workorder_id.production_state", readonly=1)
    company_id = fields.Many2one(related="workorder_id.company_id")
    ok_line = fields.Boolean(String="Ok")
    possible_workorder_ids = fields.Many2many(
        comodel_name="mrp.workorder",
        compute="_compute_possible_workorder_ids",
        string="Possible Workorders")
    worksheet = fields.Binary(
        string="Worksheet",
        related="workorder_id.worksheet",
        readonly=True)

    @api.depends("nest_id", "nest_id.main_product_id",
                 "nest_id.workcenter_id", "nest_id.workorder_ids")
    def _compute_possible_workorder_ids(self):
        workorder_obj = self.env["mrp.workorder"]
        for nest_line in self:
            nest = nest_line.nest_id
            assigned_wo = nest.workorder_ids.ids
            workorders = workorder_obj.search(
                [("main_product_id", "=", nest.main_product_id.id),
                 ("workcenter_id", "=", nest.workcenter_id.id),
                 ("id", "not in", assigned_wo),
                 ("state", "not in", ["done", "cancel"])])
            nest_line.possible_workorder_ids = [(6, 0, workorders.ids or [])]

    def nest_line_form_view(self, res_id):
        view_ref = self.env["ir.model.data"].get_object_reference(
            "mrp_workorder_grouping_by_material",
            "mrp_workorder_nest_line_form")
        view_id = view_ref and view_ref[1] or False,
        return {
            "name": "Workorder nest line",
            "domain": [],
            "res_model": "mrp.workorder.nest.line",
            "res_id": res_id,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "view_id": view_id,
            "context": {},
            "target": "new",
        }

    def button_get_previous_line(self):
        self.ensure_one()
        nest_lines = self.nest_id.nested_line_ids
        line_index = -1
        for index, line in enumerate(nest_lines):
            if self.id == line.id:
                line_index = index - 1
        res_id = nest_lines[line_index].id if line_index >= 0 else self.id
        return self.nest_line_form_view(res_id)

    def button_get_next_line(self):
        self.ensure_one()
        nest_lines = self.nest_id.nested_line_ids
        line_index = -1
        for index, line in enumerate(nest_lines):
            if self.id == line.id:
                line_index = index + 1
        if -1 < line_index < len(nest_lines):
            res_id = nest_lines[line_index].id
        else:
            res_id = self.id
        return self.nest_line_form_view(res_id)

    def get_worksheet(self):
        self.ensure_one()
        return self.workorder_id.worksheet

    def show_worksheet(self):
        self.ensure_one()
        wizard = self.env["binary.container"].create({
            "binary_field": self.get_worksheet(),
        })
        action = self.env.ref("pdf_previewer.binary_container_action")
        action_dict = action and action.read()[0] or {}
        action_dict.update({
            "name": _("Worksheet"),
            "res_id": wizard.id,
        })
        return action_dict

    def _create_assign_lot(self, code, product_id):
        if code:
            lot_obj = self.env['stock.production.lot']
            lot_id = False
            if product_id.tracking == 'serial':
                pass
            if product_id.tracking == 'lot':
                lot_id = lot_obj.search([
                    ('name', '=', code),
                    ('company_id', '=', self.env.company.id),
                    ('product_id', '=', product_id.id)], limit=1).id
            if product_id.tracking == 'none':
                return False
            if not lot_id:
                return lot_obj.create({
                    'name': code,
                    'product_id': product_id.id,
                    'company_id': self.env.company.id,
                }).id
            return lot_id

    @api.model
    def create(self, vals):
        nest_id = vals.get('nest_id')
        workorder_id = vals.get('workorder_id')
        if nest_id and workorder_id:
            nest = self.env['mrp.workorder.nest'].browse(nest_id)
            code = "{}/{}".format(nest.name or "", nest.code or "")
            product_id = self.env['mrp.workorder'].browse(
                workorder_id).product_id
            vals['finished_lot_id'] = self._create_assign_lot(code, product_id)
        return super().create(vals)

    def update_workorder_lines(self, line_values):
        for values in line_values['to_create']:
            values.pop('raw_workorder_id')
            values.update({'workorder_id': self.workorder_id.id})
            self.env['mrp.workorder.line'].create(values)
        for line in line_values['to_delete']:
            if line in self.raw_workorder_line_ids:
                line.unlink()
            else:
                self.finished_workorder_line_ids -= line
        for line, vals in line_values['to_update'].items():
            line.write(vals)

    def _write_lot_producing_qty(self):
        for n_line in self:
            if n_line.workorder_id.state not in ("done", "cancel"):
                res = {
                    "qty_producing": n_line.qty_producing,
                }
                line_values = n_line.workorder_id._update_workorder_lines()
                n_line.update_workorder_lines(line_values)
                if n_line.finished_lot_id:
                    res.update({
                        'finished_lot_id': n_line.finished_lot_id.id,
                    })
                if n_line.lot_id:
                    workorder_lines = n_line.workorder_id.raw_workorder_line_ids
                    move_line = workorder_lines.filtered(
                        lambda x: x.product_id == n_line.nest_id.main_product_id)
                    move_line.lot_id = n_line.lot_id
                if res:
                    n_line.workorder_id.write(res)

    def button_finish(self):
        for nl in self.filtered(
                lambda n: n.is_produced and n.state == "progress"):
            nl.workorder_id.with_context(from_nest=True).button_finish()

    def _check_final_product_lot(self):
        for wo in self.mapped("workorder_id"):
            if not wo._check_final_product_lots():
                UserError(_(
                    '{}: You should provide a lot/serial number for the '
                    'final product.').format(wo.name))

    def button_start(self):
        for nl in self.filtered(lambda n: n.state != "blocked"):
            nl.workorder_id.with_context(from_nest=True).button_start()

    def record_production(self):
        for nl in self:
            is_user_working = nl.workorder_id.is_user_working
            is_produced = nl.workorder_id.is_produced
            if is_user_working and nl.state == "progress" and not \
                    is_produced:
                nl._write_lot_producing_qty()
                wo = nl.workorder_id
                try:
                    if wo.current_quality_check_id.quality_state == "none":
                        wo.current_quality_check_id.do_pass()
                    wo.with_context(from_nest=True).record_production()
                except UserError as e:
                    raise UserError(_("{}: {}").format(wo.name, str(e)))
                except AttributeError:
                    # If enterprise module mrp_workorder module
                    # is not installed quality check is not necessary
                    pass

    def button_pending(self):
        for nl in self:
            is_user_working = nl.workorder_id.is_user_working
            if nl.working_state != "blocked" and is_user_working and \
                    nl.state not in ("done", "pending", "ready", "cancel"):
                nl.workorder_id.with_context(
                    from_nest=True).button_pending()

    def button_scrap(self):
        for nest_line in self:
            if nest_line.state not in ("confirmed", "cancel"):
                nest_line.workorder_id.with_context(
                    from_nest=True).button_scrap()

    def button_quality_alert(self):
        return self.workorder_id.button_quality_alert()

    def button_unblock(self):
        return self.workcenter_id.unblock()

    def button_change_ok_line(self):
        self.ok_line = not self.ok_line
        return self.nest_line_form_view(self.id)

    def open_line(self):
        self.ensure_one()
        if self.nest_id.nested_line_ids:
            view_ref = self.env["ir.model.data"].get_object_reference(
                "mrp_workorder_grouping_by_material",
                "mrp_workorder_nest_line_form")
            view_id = view_ref and view_ref[1] or False,

        return {
            "name": "Workorder nest line",
            "domain": [],
            "res_model": "mrp.workorder.nest.line",
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "view_id": view_id,
            "context": {},
            "target": "new",
        }
