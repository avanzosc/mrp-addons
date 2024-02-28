# Copyright 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval

try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None


def check_number(number):
    try:
        if isinstance(number, float) or isinstance(number, int):
            return number
        if "." in number:
            val = float(number)
        else:
            val = int(number)
        return val
    except ValueError:
        return False

def convert2str(value):
    if isinstance(value, float) or isinstance(value, int):
        new_value = str(value).strip()
        if "." in new_value:
            new_value = new_value[: new_value.index(".")]
        return new_value.strip(" \n\t")
    elif isinstance(value, tuple):
        return value[0].strip(" \n\t")
    else:
        return value.strip(" \n\t")


IMPORT_STATUS = [
    ("2validate", "To validate"),
    ("pass", "Validated"),
    ("error", "Error"),
    ("done", "Processed"),
]


class MrpBomImport(models.Model):
    _name = "mrp.bom.import"
    _description = "Import BoM from excel file"
    _order = "file_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Import name",
        compute="_compute_import_name",
        copy=False,
    )
    bom_count = fields.Integer(
        compute="_compute_bom_count",
        string="Total BoMs",
    )
    data = fields.Binary(
        string="File",
        required=True,
        copy=False,
    )
    filename = fields.Char(
        string="Filename",
        copy=False,
    )
    file_date = fields.Date(
        string="File Import Date",
        required=True,
        default=fields.Date.context_today,
        copy=False,
    )
    bom_line_import_ids = fields.One2many(
        comodel_name="mrp.bom.line.import",
        inverse_name="bom_import_id",
        string="BoM Component Lines",
        copy=False,
    )
    state = fields.Selection(
        selection=IMPORT_STATUS,
        compute="_compute_state",
        string="Status",
    )
    log_info = fields.Text(
        string="Log Info",
        compute="_compute_log_info",
    )
    product_found_by_code = fields.Boolean(
        string="Product Found By Code",
        default=False)

    def _get_import_lines(self):
        return self.mapped("bom_line_import_ids")

    @api.depends("filename", "file_date")
    def _compute_import_name(self):
        for file_import in self:
            file_import.name = "{} - {}".format(
                file_import.filename, file_import.file_date
            )

    @api.depends(
        "bom_line_import_ids",
        "bom_line_import_ids.product_id",
        "bom_line_import_ids.bom_id",
    )
    def _compute_bom_count(self):
        for bom_import in self:
            lines = bom_import._get_import_lines()
            bom_import.bom_count = len(lines.mapped("bom_id"))

    @api.depends(
        "bom_line_import_ids",
        "bom_line_import_ids.state",
    )
    def _compute_state(self):
        for bom_import in self:
            lines = bom_import._get_import_lines()
            line_states = lines.mapped("state")
            if line_states and any([state == "error" for state in line_states]):
                bom_import.state = "error"
            elif line_states and all([state == "done" for state in line_states]):
                bom_import.state = "done"
            elif line_states and all([state == "pass" for state in line_states]):
                bom_import.state = "pass"
            else:
                bom_import.state = "2validate"

    @api.depends(
        "bom_line_import_ids",
        "bom_line_import_ids.log_info",
    )
    def _compute_log_info(self):
        for bom_import in self:
            lines = bom_import._get_import_lines()
            logged_lines = lines.filtered("log_info")
            if logged_lines:
                bom_import.log_info = "\n".join(logged_lines.mapped("log_info"))
            else:
                bom_import.log_info = ""

    def action_bom_import_boms(self):
        action = self.env.ref("mrp.mrp_bom_form_action")
        action_dict = action and action.read()[0]
        lines = self._get_import_lines()
        domain = expression.AND(
            [
                [("id", "in", lines.mapped("bom_id").ids)],
                safe_eval(action.domain or "[]"),
            ]
        )
        action_dict.update({"domain": domain})
        return action_dict

    def action_bom_import_bom_lines(self):
        action = self.env.ref("mrp_bom_import.mrp_bom_line_action")
        action_dict = action and action.read()[0]
        lines = self._get_import_lines()
        domain = expression.AND(
            [
                [("id", "in", lines.mapped("bom_line_id").ids)],
                safe_eval(action.domain or "[]"),
            ]
        )
        action_dict.update({"domain": domain})
        return action_dict

    def action_import_bom(self):
        self.ensure_one()
        (self._get_import_lines()).unlink()
        book = base64.decodebytes(self.data)
        reader = xlrd.open_workbook(file_contents=book)
        try:
            sheet_list = reader.sheet_names()
            for sheet_name in sheet_list:
                sheet = reader.sheet_by_name(sheet_name)
                bom_import_line_obj = self.env["mrp.bom.line.import"]
                keys = [c.value for c in sheet.row(0)]
                for counter in range(1, sheet.nrows):
                    row_values = sheet.row_values(counter, 0, end_colx=sheet.ncols)
                    values = dict(zip(keys, row_values))
                    line_data = self._get_line_values(values)
                    if line_data:
                        bom_import_line_obj.create(line_data)
        except Exception:
            raise ValidationError(_("This is not a valid file."))

    def _get_line_values(self, row_values):
        self.ensure_one()
        if (
            not row_values.get("Product Name")
            and not row_values.get("Product Code")
            and not row_values.get("Quantity", 0.0)
        ):
            return {}
        values = {
            "bom_ref": convert2str(row_values.get("BoM Ref", "")),
            "product_name": convert2str(row_values.get("Product Name", "")),
            "product_ref": convert2str(row_values.get("Product Code", "")),
            "quantity": check_number(row_values.get("Quantity", 0.0)),
            "bom_code": convert2str(row_values.get("Parent Code", "")),
            "bom_name": convert2str(row_values.get("Parent Name", "")),
            "parent_qty": check_number(row_values.get("Parent Qty", 0.0)),
        }
        values.update(
            {
                "bom_import_id": self.id,
            }
        )
        return values

    def action_validate_lines(self):
        lines = (self._get_import_lines()).filtered(
            lambda x: x.state not in ("done"))
        lines.action_validate_lines()

    def action_process_lines(self):
        lines = (self._get_import_lines()).filtered(
            lambda x: x.state == "pass")
        lines.action_process_lines()

    def button_open_bom_component_import_line(self):
        self.ensure_one()
        return {
            "name": _("Component Import Lines"),
            "type": "ir.actions.act_window",
            "res_model": self.bom_line_import_ids._name,
            "view_mode": "tree",
            "view_id": self.env.ref(
                "mrp_bom_import.mrp_bom_line_component_import_view_tree"
            ).id,
            "target": "current",
            "domain": [("id", "in", self.bom_line_import_ids.ids)],
            "context": {
                "default_bom_import_id": self.id,
            },
        }


class MrpBomLineImport(models.Model):
    _name = "mrp.bom.line.import"
    _description = "Import BoM lines"

    bom_import_id = fields.Many2one(
        comodel_name="mrp.bom.import",
        string="BoM Import",
        ondelete="cascade",
    )
    product_name = fields.Char(string="Product name")
    product_ref = fields.Char(string="Product code")
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    quantity = fields.Float(string="Quantity")
    bom_ref = fields.Char(string="BoM Ref")
    bom_code = fields.Char(string="BoM code")
    bom_name = fields.Char(string="BoM Name")
    bom_product_id = fields.Many2one(
        string="Parent Product",
        comodel_name="product.product")
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="BoM",
    )
    bom_line_id = fields.Many2one(
        string="BoM Line",
        comodel_name="mrp.bom.line")
    log_info = fields.Text(string="Log Info")
    state = fields.Selection(
        selection=IMPORT_STATUS,
        string="Status",
        default="2validate",
    )
    parent_product_bom_count = fields.Integer(
        string="Parent Bom Qty",
        related="bom_product_id.bom_count",
        store=True)
    parent_qty = fields.Float(string="Parent Quantity")

    def _check_product(self):
        self.ensure_one()
        log_info = ""
        if self.product_id:
            return self.product_id, log_info
        product_obj = self.env["product.product"]
        search_domain = [("name", "=", self.product_name)]
        if self.product_ref:
            search_domain = expression.AND(
                [[("default_code", "=", self.product_ref)], search_domain]
            )
        if self.bom_import_id.product_found_by_code:
            search_domain = [("default_code", "=", self.product_ref)]
        products = product_obj.search(search_domain)
        if not products:
            products = False
            log_info = _("Error: Product not found.")
        elif len(products) != 1:
            products = False
            log_info = _("Error: More than one product found.")
        return products, log_info

    def _check_bom_product(self):
        self.ensure_one()
        log_info = ""
        if self.bom_product_id:
            return self.bom_product_id, log_info
        product_obj = self.env["product.product"]
        search_domain = [("name", "=", self.bom_name)]
        if self.bom_code:
            search_domain = expression.AND(
                [[("default_code", "=", self.bom_code)], search_domain]
            )
        if self.bom_import_id.product_found_by_code:
            search_domain = [("default_code", "=", self.bom_code)]
        products = product_obj.search(search_domain)
        if not products:
            products = False
            log_info = _("Error: BoM product not found.")
        elif len(products) != 1:
            products = False
            log_info = _("Error: More than one BoM product found.")
        return products, log_info

    def action_validate_lines(self):
        for line in self.filtered(lambda x: x.state not in ("done")):
            line_vals = {}
            log_info = ""
            product = bom_product = bom = False
            product, product_log_info = line._check_product()
            if product_log_info:
                log_info += product_log_info
            bom_product, bom_product_log_info = line._check_bom_product()
            if bom_product_log_info:
                log_info += bom_product_log_info
            if not line.quantity:
                log_info += _("Error: Quantity cannot be 0.")
            state = "error" if log_info else "pass"
            line_vals.update(
                {
                    "product_id": product and product.id,
                    "bom_product_id": bom_product and bom_product.id,
                    "bom_id": bom and bom.id,
                    "state": state,
                    "log_info": log_info,
                }
            )
            line.write(line_vals)

    def _create_bom(self):
        self.ensure_one()
        bom = self.env["mrp.bom"].create({
            "product_tmpl_id": self.bom_product_id.product_tmpl_id.id,
            "code": self.bom_ref,
            "product_qty": self.parent_qty,
            "product_uom_id": self.bom_product_id.uom_id.id})
        return bom

    def generate_bom_line_values(self):
        self.ensure_one()
        bom_line = {
            "product_id": self.product_id.id,
            "product_qty": self.quantity,
            "product_uom_id": self.product_id.uom_id.id}
        return bom_line

    def action_process_lines(self):
        bom_product = []
        for line in self.filtered(lambda x: x.state == "pass"):
            log_info = ""
            bom = False
            if not line.bom_id and line.bom_product_id and line.bom_product_id not in bom_product:
                state = "2validate"
                same_parent = line.bom_import_id.bom_line_import_ids.filtered(
                    lambda c: c.bom_product_id == line.bom_product_id)
                if any([state.state == "error" for state in same_parent]):
                    log_info = _("Error: There is another line with the " +
                              "same parent product errors.")
                    state = "error"
                else:
                    bom = line._create_bom()
                    for l in same_parent:
                        bom_line_values = l.generate_bom_line_values()
                        bom_line_values.update({"bom_id": bom.id})
                        bom_line = self.env["mrp.bom.line"].create(
                            bom_line_values)
                        l.write({
                            "bom_id": bom.id,
                            "bom_line_id": bom_line.id,
                            "state": "done"})
                    state = "done"
                line.write(
                    {
                        "state": state,
                        "log_info": log_info,
                    }
                )
