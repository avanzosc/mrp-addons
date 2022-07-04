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
    products_count = fields.Integer(
        compute="_compute_products_count",
        string="Total Products",
    )
    bom_count = fields.Integer(
        compute="_compute_products_count",
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
    # import_line_ids = fields.One2many(
    #     comodel_name="mrp.bom.line.import",
    #     inverse_name="bom_import_id",
    #     string="Import Lines",
    #     copy=False,
    # )
    bom_import_ids = fields.One2many(
        comodel_name="mrp.bom.line.import",
        inverse_name="bom_import_id",
        string="BoM Lines",
        copy=False,
    )
    bom_line_import_ids = fields.One2many(
        comodel_name="mrp.bom.line.import",
        inverse_name="bom_line_import_id",
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

    def _get_import_lines(self):
        return self.mapped("bom_import_ids") | self.mapped("bom_line_import_ids")

    @api.depends("filename", "file_date")
    def _compute_import_name(self):
        for file_import in self:
            file_import.name = "{} - {}".format(
                file_import.filename, file_import.file_date
            )

    @api.depends(
        "bom_import_ids",
        "bom_import_ids.product_id",
        "bom_import_ids.bom_id",
        "bom_line_import_ids",
        "bom_line_import_ids.product_id",
        "bom_line_import_ids.bom_id",
    )
    def _compute_products_count(self):
        for bom_import in self:
            lines = bom_import._get_import_lines()
            bom_import.products_count = len(lines.mapped("product_id"))
            bom_import.bom_count = len(lines.mapped("bom_id"))

    @api.depends(
        "bom_import_ids",
        "bom_import_ids.state",
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
        "bom_import_ids",
        "bom_import_ids.log_info",
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

    def action_bom_import_products(self):
        action = self.env.ref("product.product_normal_action")
        action_dict = action and action.read()[0]
        lines = self._get_import_lines()
        domain = expression.AND(
            [
                [("id", "in", lines.mapped("product_id").ids)],
                safe_eval(action.domain or "[]"),
            ]
        )
        action_dict.update({"domain": domain})
        return action_dict

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
            not row_values.get("name")
            and not row_values.get("code")
            and not row_values.get("qty", 0.0)
        ):
            return {}
        values = {
            "product_name": row_values.get("name", ""),
            "product_ref": row_values.get("code", ""),
            "quantity": check_number(row_values.get("qty", 0.0)),
            "weight": check_number(row_values.get("weight", 0.0)),
            "bom_code": row_values.get("parent_code", ""),
        }
        if row_values.get("parent_code"):
            values.update(
                {
                    "bom_line_import_id": self.id,
                }
            )
        else:
            values.update(
                {
                    "bom_import_id": self.id,
                }
            )
        return values

    def action_validate_lines(self):
        lines = (self._get_import_lines()).filtered(
            lambda x: x.state not in ("done", "pass")
        )
        lines.filtered(lambda l: not l.bom_code).action_validate_lines()
        lines.filtered("bom_code").action_validate_lines()

    def action_process_lines(self):
        lines = (self._get_import_lines()).filtered(lambda x: x.state == "pass")
        lines.filtered(lambda l: not l.bom_code).action_process_lines()
        lines.filtered("bom_code").action_process_lines()

    def button_open_bom_import_line(self):
        self.ensure_one()
        return {
            "name": _("BoM Import Lines"),
            "type": "ir.actions.act_window",
            "res_model": self.bom_import_ids._name,
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("id", "in", self.bom_import_ids.ids)],
            "context": {
                "default_bom_import_id": self.id,
            }
        }

    def button_open_bom_component_import_line(self):
        self.ensure_one()
        return {
            "name": _("Component Import Lines"),
            "type": "ir.actions.act_window",
            "res_model": self.bom_line_import_ids._name,
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("id", "in", self.bom_line_import_ids.ids)],
            "context": {
                "default_bom_line_import_id": self.id,
            }
        }


class MrpBomLineImport(models.Model):
    _name = "mrp.bom.line.import"
    _description = "Import BoM lines"

    bom_import_id = fields.Many2one(
        comodel_name="mrp.bom.import",
        string="BoM Import",
        ondelete="cascade",
    )
    bom_line_import_id = fields.Many2one(
        comodel_name="mrp.bom.import",
        string="BoM Import",
        ondelete="cascade",
    )
    quantity = fields.Float(string="Quantity")
    product_name = fields.Char(string="Product name")
    product_ref = fields.Char(string="Product code")
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    weight = fields.Float(string="Weight")
    bom_code = fields.Char(string="BoM code")
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="BoM",
    )
    parent_line_id = fields.Many2one(
        comodel_name="mrp.bom.line.import",
        string="BoM parent line",
    )
    categ_name = fields.Char(string="Category name")
    category_id = fields.Many2one(
        comodel_name="product.category",
        string="Category",
    )
    log_info = fields.Text(string="Log Info")
    state = fields.Selection(
        selection=IMPORT_STATUS,
        string="Status",
        default="2validate",
    )

    def _check_product(self):
        self.ensure_one()
        product_obj = self.env["product.product"]
        search_domain = [("name", "=", self.product_name)]
        log_info = ""
        if self.product_ref:
            search_domain = expression.AND(
                [[("default_code", "=", self.product_ref)], search_domain]
            )
        products = product_obj.search(search_domain)
        if not products:
            log_info = _("Error: Product not found")
        elif len(products) != 1:
            log_info = _("Error: More than one product already exist")
        return products[:1], log_info

    def _check_bom_id(self, product=False):
        self.ensure_one()
        bom = bom_obj = self.env["mrp.bom"]
        log_info = ""
        if self.bom_code:
            bom = self.search(
                [
                    ("product_name", "=", self.bom_code),
                    ("bom_import_id", "=", self.bom_line_import_id.id),
                ]
            )
            if not bom:
                log_info = _("Error: BoM not found")
            elif len(bom) != 1:
                log_info = _("Error: More than one BoM already exist")
            else:
                log_info = bom.log_info
        elif self.product_id:
            bom = bom_obj.search(
                [
                    ("product_id", "=", self.product_id.id),
                ]
            )
            if bom:
                log_info = _("Error: BoM already exist")
        return bom[:1], log_info

    def action_validate_lines(self):
        for line in self.filtered(lambda x: x.state not in ("done", "pass")):
            line_vals = {}
            if not line.product_id and (line.product_ref or line.product_name):
                product, product_log_info = line._check_product()
                line_vals.update(
                    {
                        "state": "error" if product_log_info else "pass",
                        "log_info": product_log_info,
                    }
                )
                if product_log_info:
                    line.write(line_vals)
                    continue
                else:
                    line.product_id = product
            bom, bom_log_info = line._check_bom_id()
            line_vals.update(
                {
                    "state": "error" if bom_log_info else "pass",
                    "log_info": bom_log_info,
                }
            )
            if bom_log_info:
                line.write(line_vals)
                continue
            else:
                if line.bom_code:
                    line.write(
                        {
                            "parent_line_id": bom.id,
                            "bom_id": bom.bom_id.id,
                        }
                    )
                else:
                    line.bom_id = bom
            if not line.quantity:
                line_vals.update(
                    {
                        "state": "error",
                        "log_info": _("Error: Quantity cannot be 0"),
                    }
                )
            line.write(line_vals)

    def generate_bom_values(self):
        self.ensure_one()
        return {
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "product_id": self.product_id.id,
            "product_qty": self.quantity,
        }

    def generate_bom_line_values(self):
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "product_qty": self.quantity,
            "bom_id": self.parent_line_id.bom_id.id,
        }

    def action_process_lines(self):
        bom_obj = self.env["mrp.bom"]
        bom_line_obj = self.env["mrp.bom.line"]
        for line in self.filtered(lambda x: x.state == "pass"):
            if line.parent_line_id and line.parent_line_id.bom_id:
                bom = line.parent_line_id.bom_id
                bom_line_values = line.generate_bom_line_values()
                bom_line_obj.create(bom_line_values)
            else:
                bom_values = line.generate_bom_values()
                bom = bom_obj.create(bom_values)
            line.write(
                {
                    "bom_id": bom.id,
                    "state": "done",
                    "log_info": "",
                }
            )
