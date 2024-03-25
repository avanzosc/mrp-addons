# Copyright 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base_import_wizard.models.base_import import check_number, convert2str


class MrpBomImport(models.Model):
    _name = "mrp.bom.import"
    _inherit = "base.import"
    _description = "Import BoM from excel file"

    bom_count = fields.Integer(
        compute="_compute_bom_count",
        string="Total BoMs",
    )
    import_line_ids = fields.One2many(
        comodel_name="mrp.bom.line.import",
    )
    product_found_by_code = fields.Boolean(
        default=False,
    )

    @api.depends(
        "import_line_ids",
        "import_line_ids.bom_id",
    )
    def _compute_bom_count(self):
        for bom_import in self:
            bom_import.bom_count = len(bom_import.mapped("import_line_ids.bom_id"))

    def _get_line_values(self, row_values, datemode=False):
        self.ensure_one()
        values = super()._get_line_values(row_values, datemode=datemode)
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
                "quantity": check_number(row_values.get("Quantity", 0.0)),
                "bom_code": convert2str(row_values.get("Parent Code", "")),
                "bom_name": convert2str(row_values.get("Parent Name", "")),
                "parent_qty": check_number(row_values.get("Parent Qty", 0.0)),
            }
        )
        return values

    def button_open_bom(self):
        self.ensure_one()
        contacts = self.mapped("import_line_ids.bom_id")
        action = self.env.ref("mrp.mrp_bom_form_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND(
            [[("id", "in", contacts.ids)], safe_eval(action.domain or "[]")]
        )
        action_dict.update({"domain": domain})
        return action_dict

    # def button_open_bom_line(self):
    #     self.ensure_one()
    #     contacts = self.mapped("import_line_ids.partner_id")
    #     action = self.env.ref("contacts.action_contacts")
    #     action_dict = action.read()[0] if action else {}
    #     domain = expression.AND(
    #         [[("id", "in", contacts.ids)], safe_eval(action.domain or "[]")]
    #     )
    #     action_dict.update({"domain": domain})
    #     return action_dict


class MrpBomLineImport(models.Model):
    _name = "mrp.bom.line.import"
    _inherit = "base.import.line"
    _description = "Import BoM lines"

    import_id = fields.Many2one(
        comodel_name="mrp.bom.import",
    )
    product_name = fields.Char(string="Product name")
    product_ref = fields.Char(string="Product code")
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    quantity = fields.Float()
    bom_ref = fields.Char(string="BoM Refernce")
    bom_code = fields.Char(string="BoM Code")
    bom_name = fields.Char(string="BoM Name")
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
    parent_qty = fields.Float(string="Parent Quantity")

    def _action_validate(self):
        update_values = super()._action_validate()
        log_infos = []
        product = self.product_id
        if not product:
            product, log_info_product = self._check_product(
                self.product_name, self.product_ref
            )
            if log_info_product:
                log_infos.append(log_info_product)
        bom_product = self.bom_product_id
        if self.bom_name and bom_product:
            bom_product, log_info_bom_product = self._check_product(
                self.bom_name, self.bom_code
            )
            if log_info_bom_product:
                log_infos.append(log_info_bom_product)
        state = "error" if log_infos else "pass"
        action = "create" if state != "error" else "nothing"
        update_values.update(
            {
                "product_id": product and product.id,
                "bom_product_id": bom_product and bom_product.id,
                "log_info": "\n".join(log_infos),
                "state": state,
                "action": action,
            }
        )
        return update_values

    def _action_process(self):
        update_values = super()._action_process()
        # if self.action != "nothing":
        return update_values

    def _check_product(self, product_name, product_code=False):
        self.ensure_one()
        log_info = ""
        # if self.product_id:
        #     return self.product_id, log_info
        product_obj = self.env["product.product"]
        search_domain = [("name", "=", product_name)]
        if product_code:
            search_domain = expression.AND(
                [[("default_code", "=", product_code)], search_domain]
            )
        if self.import_id.product_found_by_code:
            search_domain = [("default_code", "=", product_code)]
        products = product_obj.search(search_domain)
        if not products:
            log_info = _("Product not found.")
        elif len(products) != 1:
            products = False
            log_info = _("More than one product found.")
        return products, log_info

    def _create_bom(self):
        self.ensure_one()
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.bom_product_id.product_tmpl_id.id,
                "code": self.bom_ref,
                "product_qty": self.parent_qty,
                "product_uom_id": self.bom_product_id.uom_id.id,
            }
        )
        return bom

    def generate_bom_line_values(self):
        self.ensure_one()
        bom_line = {
            "product_id": self.product_id.id,
            "product_qty": self.quantity,
            "product_uom_id": self.product_id.uom_id.id,
        }
        return bom_line

    # def action_process_lines(self):
    #     bom_product = []
    #     for line in self.filtered(lambda x: x.state == "pass"):
    #         log_info = ""
    #         bom = False
    #         if (not line.bom_id and line.bom_product_id and line.bom_product_id not
    #                 in bom_product):
    #             state = "2validate"
    #             same_parent = line.bom_import_id.bom_line_import_ids.filtered(
    #                 lambda c: c.bom_product_id == line.bom_product_id)
    #             if any([state.state == "error" for state in same_parent]):
    #                 log_info = _("Error: There is another line with the " +
    #                           "same parent product errors.")
    #                 state = "error"
    #             else:
    #                 bom = line._create_bom()
    #                 for l in same_parent:
    #                     bom_line_values = l.generate_bom_line_values()
    #                     bom_line_values.update({"bom_id": bom.id})
    #                     bom_line = self.env["mrp.bom.line"].create(
    #                         bom_line_values)
    #                     l.write({
    #                         "bom_id": bom.id,
    #                         "bom_line_id": bom_line.id,
    #                         "state": "done"})
    #                 state = "done"
    #             line.write(
    #                 {
    #                     "state": state,
    #                     "log_info": log_info,
    #                 }
    #             )
