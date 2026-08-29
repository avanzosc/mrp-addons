# Copyright 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base_import_wizard.models.base_import import check_number, convert2str


class MrpBomImport(models.Model):
    _name = "mrp.bom.import"
    _inherit = "base.import"
    _description = "Import BoM from excel file"
    _order = "file_date desc"

    import_line_ids = fields.One2many(
        comodel_name="mrp.bom.import.line",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
    )
    bom_count = fields.Integer(
        string="# BoMs",
        compute="_compute_bom_count",
    )
    bom_line_count = fields.Integer(
        string="# Components",
        compute="_compute_bom_count",
    )
    product_found_by_code = fields.Boolean(
        default=False,
    )

    def _get_line_values(self, row_values, datemode=False):
        self.ensure_one()
        values = super()._get_line_values(row_values, datemode=datemode)
        if row_values:
            if (
                not row_values.get("Product Name")
                and not row_values.get("Product Code")
                and not row_values.get("Quantity", 0.0)
            ):
                return {}
            values.update(
                {
                    "bom_ref": convert2str(row_values.get("BoM Ref", "")),
                    "product_name": convert2str(row_values.get("Product Name", "")),
                    "product_ref": convert2str(row_values.get("Product Code", "")),
                    "quantity": check_number(row_values.get("Quantity", 1.0)),
                    "bom_code": convert2str(row_values.get("Parent Code", "")),
                    "bom_name": convert2str(row_values.get("Parent Name", "")),
                    "parent_qty": check_number(row_values.get("Parent Qty", 1.0)),
                }
            )
        return values

    def _compute_bom_count(self):
        for record in self:
            record.update(
                {
                    "bom_count": len(record.mapped("import_line_ids.bom_id")),
                    "bom_line_count": len(record.mapped("import_line_ids.bom_line_id")),
                }
            )

    def button_open_boms(self):
        self.ensure_one()
        boms = self.mapped("import_line_ids.bom_id")
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        action["domain"] = expression.AND(
            [[("id", "in", boms.ids)], safe_eval(action.get("domain") or "[]")]
        )
        action["context"] = dict(self._context, create=False)
        return action

    def button_open_bom_lines(self):
        self.ensure_one()
        bom_lines = self.mapped("import_line_ids.bom_line_id")
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_bom_component_menu.mrp_bom_form_action2"
        )
        action["domain"] = expression.AND(
            [[("id", "in", bom_lines.ids)], safe_eval(action.get("domain") or "[]")]
        )
        action["context"] = dict(self._context, create=False)
        return action


class MrpBomLineImport(models.Model):
    _name = "mrp.bom.import.line"
    _inherit = "base.import.line"
    _description = "Import BoM lines"

    import_id = fields.Many2one(
        comodel_name="mrp.bom.import",
    )
    action = fields.Selection(
        selection_add=[("create", "Create")],
        ondelete={"create": "set default"},
    )
    product_name = fields.Char(
        string="Product name",
    )
    product_ref = fields.Char(
        string="Product code",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    quantity = fields.Float(
        default=1.0,
    )
    bom_ref = fields.Char(
        string="BoM Ref",
    )
    bom_code = fields.Char(
        string="BoM code",
    )
    bom_name = fields.Char(
        string="BoM Name",
    )
    bom_product_id = fields.Many2one(
        string="Parent Product",
        comodel_name="product.product",
    )
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="BoM",
    )
    bom_line_id = fields.Many2one(
        string="BoM Line",
        comodel_name="mrp.bom.line",
    )
    parent_product_bom_count = fields.Integer(
        string="Parent Bom Qty",
        related="bom_product_id.bom_count",
        store=True,
    )
    parent_qty = fields.Float(
        string="Parent Quantity",
        default=1.0,
    )

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
        if self.import_id.product_found_by_code:
            search_domain = [("default_code", "=", self.product_ref)]
        products = product_obj.search(search_domain)
        if not products:
            products = False
            log_info = _("Product not found.")
        elif len(products) != 1:
            products = False
            log_info = _("More than one product found.")
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
        if self.import_id.product_found_by_code:
            search_domain = [("default_code", "=", self.bom_code)]
        products = product_obj.search(search_domain)
        if not products:
            products = False
            log_info = _("BoM product not found.")
        elif len(products) != 1:
            products = False
            log_info = _("More than one BoM product found.")
        return products, log_info

    def _action_validate(self):
        self.ensure_one()
        update_values = super()._action_validate()
        log_infos = []
        product, product_log_info = self._check_product()
        if product_log_info:
            log_infos.append(product_log_info)
        bom_product, bom_product_log_info = self._check_bom_product()
        if bom_product_log_info:
            log_infos.append(bom_product_log_info)
        if not self.quantity:
            log_infos.append(_("Quantity must be defined."))
        if product and bom_product and product.id == bom_product.id:
            log_infos.append(_("Product and BOM product are the same"))
        state = "error" if log_infos else "pass"
        update_values.update(
            {
                "product_id": product and product.id,
                "bom_product_id": bom_product and bom_product.id,
                "state": state,
                "log_info": "\n".join(log_infos),
            }
        )
        return update_values

    def _create_bom(self):
        self.ensure_one()

        bom_ref = self.bom_ref
        if not bom_ref:
            bom_ref = self.bom_product_id.default_code or self.bom_product_id.name
        if self.bom_import_id.bom_count:
            bom_ref = f"{bom_ref}-{self.bom_import_id.bom_count + 1}"

        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.bom_product_id.product_tmpl_id.id,
                "code": bom_ref,
                "product_qty": self.parent_qty,
                "product_uom_id": self.bom_product_id.uom_id.id,
            }
        )
        return bom

    def _bom_line_values(self):
        return {
            "product_id": self.product_id and self.product_id.id,
            "product_qty": self.quantity,
            "product_uom_id": self.product_id
            and self.product_id.uom_id
            and self.product_id.uom_id.id,
        }

    def _action_process(self):
        update_values = super()._action_process()
        if self.action != "nothing":
            if self.import_id.company_id:
                self = self.with_company(self.import_id.company_id)
            if self.action == "create":
                partner, log_info = self._create_partner()
            elif self.action == "update":
                partner, log_info = self._update_partner()
            state = "error" if log_info else "done"
            update_values.update(
                {
                    "partner_id": partner and partner.id,
                    "log_info": log_info,
                    "state": state,
                }
            )
        return update_values

    def action_process_lines(self):
        bom_product = []
        for line in self.filtered(lambda x: x.state == "pass"):
            log_info = ""
            bom = False
            if (
                not line.bom_id
                and line.bom_product_id
                and line.bom_product_id not in bom_product
            ):
                state = "2validate"
                same_parent = line.bom_import_id.bom_line_import_ids.filtered(
                    lambda c, line=line: c.bom_product_id == line.bom_product_id
                )
                if any([state.state == "error" for state in same_parent]):
                    log_info = _(
                        "Error: There is another line with the same parent product"
                        " errors."
                    )
                    state = "error"
                else:
                    bom = line._create_bom()
                    for ln in same_parent:
                        bom_line_values = ln._bom_line_values()
                        bom_line_values.update({"bom_id": bom.id})
                        bom_line = self.env["mrp.bom.line"].create(bom_line_values)
                        ln.write(
                            {
                                "bom_id": bom.id,
                                "bom_line_id": bom_line.id,
                                "state": "done",
                            }
                        )
                    state = "done"
                line.write(
                    {
                        "state": state,
                        "log_info": log_info,
                    }
                )
