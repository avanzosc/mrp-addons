# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import tempfile

from PyPDF2 import PdfFileMerger

from .mrp_workorder_nest import NEST_STATE
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpWorkorderNestLine(models.Model):
    _name = "mrp.workorder.nest.line"
    _description = "Nested Lines"

    def _get_selection_workorder_state(self):
        return self.env["mrp.workorder"].fields_get(
            allfields=["state"])["state"]["selection"]

    def default_workorder_state(self):
        default_dict = self.env["mrp.workorder"].default_get(["state"])
        return default_dict.get("state")

    nest_id = fields.Many2one(
        comodel_name="mrp.workorder.nest",
        required=True)
    # related_qty_producing = fields.Float(
    #     related="workorder_id.qty_producing")
    # related_finished_lot_id = fields.Many2one(
    #     comodel_name="stock.production.lot",
    #     related="workorder_id.finished_lot_id")
    qty_producing = fields.Float(
        string="Quantity Producing",
        default=1.0,
        digits="Product Unit of Measure",
        copy=True)
    finished_lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot/Serial Number",
        domain="[('product_id', '=', product_id)]")
    # lot_id = fields.Many2one(
    #     comodel_name="stock.production.lot",
    #     domain="[('product_id', '=', nest_id.main_product_id.id)]")
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
    finished_qty = fields.Float(
        compute="_compute_finished_qty")
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
        string="Status",
        compute="_compute_state",
        selection=_get_selection_workorder_state,
        default=default_workorder_state)
    workorder_state = fields.Selection(
        string="Workorder Status",
        related="workorder_id.state",
        readonly=True)
    working_state = fields.Selection(
        string="Workcenter Status",
        related="workorder_id.working_state",
        readonly=True)
    is_produced = fields.Boolean(
        related="workorder_id.is_produced")
    is_user_working = fields.Boolean(
        related="workorder_id.is_user_working")
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

    @api.depends("workorder_id", "workorder_id.production_id")
    def _compute_finished_qty(self):
        for line in self:
            production = line.workorder_id.production_id
            line.finished_qty = sum(
                production.mapped(
                    "move_finished_ids.move_line_ids").filtered(
                        lambda m: m.product_id == line.product_id
                        and m.lot_id == line.finished_lot_id
                    ).mapped("qty_done"))

    def _compute_state(self):
        for line in self:
            workorder = line.workorder_id
            qty_done = sum(workorder.finished_workorder_line_ids.filtered(
                    lambda m: m.product_id == line.product_id
                    and m.lot_id == line.finished_lot_id
                ).mapped("qty_done"))
            qty_done += sum(workorder.production_id.mapped(
                "move_finished_ids.move_line_ids").filtered(
                    lambda m: m.product_id == line.product_id
                    and m.lot_id == line.finished_lot_id
                ).mapped("qty_done"))
            if line.qty_producing <= qty_done:
                line.state = "done"
            else:
                line.state = workorder.state

    def nest_line_form_view(self, res_id):
        view_ref = self.env["ir.model.data"].get_object_reference(
            "mrp_workorder_grouping_by_material",
            "mrp_workorder_nest_line_wizard_form")
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

    def get_worksheets(self):
        lines = self.filtered("workorder_id.worksheet")
        return lines.mapped("workorder_id.worksheet")

    def show_worksheets(self):
        self.ensure_one()
        worksheets = self.get_worksheets()
        if not worksheets:
            return
        wizard = self.env["binary.container"].create({
            "binary_field": (
                worksheets[0] if isinstance(worksheets, list) else worksheets),
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
                if n_line.nest_id.lot_id:
                    workorder_lines = n_line.workorder_id.raw_workorder_line_ids
                    move_line = workorder_lines.filtered(
                        lambda x: x.product_id == n_line.nest_id.main_product_id)
                    move_line.lot_id = n_line.nest_id.lot_id
                if res:
                    n_line.workorder_id.write(res)

    def button_finish(self):
        for nl in self.filtered(
                lambda n: n.is_produced and n.workorder_state == "progress"):
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
            nl.state = nl.workorder_id.state

    def record_production(self):
        for nl in self:
            is_user_working = nl.workorder_id.is_user_working
            is_produced = nl.workorder_id.is_produced
            if (is_user_working and nl.workorder_id.state == "progress" and
                    not is_produced):
                nl._write_lot_producing_qty()
                wo = nl.workorder_id
                try:
                    if wo.current_quality_check_id.quality_state == "none":
                        wo.current_quality_check_id.do_pass()
                except AttributeError:
                    # If enterprise module mrp_workorder module
                    # is not installed quality check is not necessary
                    pass
                try:
                    wo.with_context(from_nest=True).record_production()
                    qty_done = sum(wo.finished_workorder_line_ids.filtered(
                        lambda l: l.product_id == nl.product_id and
                        l.lot_id == nl.finished_lot_id).mapped("qty_done"))
                    if nl.qty_producing <= qty_done:
                        nl.state = "done"
                except UserError as e:
                    raise UserError(_("{}: {}").format(wo.name, str(e)))

    def button_pending(self):
        for nl in self:
            is_user_working = nl.workorder_id.is_user_working
            if (nl.working_state != "blocked" and is_user_working and
                    nl.workorder_id.state not in (
                        "done", "pending", "ready", "cancel")):
                nl.workorder_id.with_context(
                    from_nest=True).button_pending()

    def button_scrap(self):
        for nest_line in self.filtered(
                lambda l: l.workorder_state not in ("confirmed", "cancel")):
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
        return self.nest_line_form_view(self.id)
