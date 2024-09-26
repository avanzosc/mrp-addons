# Copyright 2024 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base_import_wizard.models.base_import import convert2str


class MrpWorkcenterRoutingImport(models.Model):
    _name = "mrp.routing.workcenter.import"
    _description = "Import Workcenter Routing from excel file"
    _inherit = "base.import"

    import_line_ids = fields.One2many(
        comodel_name="mrp.routing.workcenter.import.line",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        index=True,
        required=True,
        default=lambda self: self.env.company.id,
        states={"done": [("readonly", True)]},
    )
    product_found_by_code = fields.Boolean(
        default=False,
        states={"done": [("readonly", True)]},
    )
    bom_count = fields.Integer(
        compute="_compute_bom_count",
        string="Total BoMs",
    )
    operation_count = fields.Integer(
        compute="_compute_operation_count",
        string="Total Operations",
    )

    def _compute_bom_count(self):
        for record in self:
            record.bom_count = len(record.mapped("import_line_ids.bom_id"))

    def _compute_operation_count(self):
        for record in self:
            record.operation_count = len(record.mapped("import_line_ids.operation_id"))

    def _get_line_values(self, row_values, datemode=False):
        self.ensure_one()
        values = super()._get_line_values(row_values, datemode=datemode)
        if row_values:
            bom_ref = row_values.get("BoM Ref", "")
            operation_name = row_values.get("Operation", "")
            workcenter_name = row_values.get("Workcenter", "")
            product_code = row_values.get("Product Code", "")
            product_name = row_values.get("Product Name", "")
            log_info = ""
            values.update(
                {
                    "bom_ref": convert2str(bom_ref),
                    "operation_name": convert2str(operation_name),
                    "workcenter_name": convert2str(workcenter_name),
                    "product_code": convert2str(product_code),
                    "product_name": convert2str(product_name),
                    "log_info": log_info,
                }
            )
        return values

    def button_open_boms(self):
        self.ensure_one()
        boms = self.mapped("import_line_ids.bom_id")
        action = self.env.ref("mrp.mrp_bom_form_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND(
            [[("id", "=", boms.ids)], safe_eval(action.domain or "[]")]
        )
        action_dict.update({"domain": domain})
        return action_dict

    def button_open_operations(self):
        self.ensure_one()
        operation = self.mapped("import_line_ids.operation_id")
        action = self.env.ref("mrp.mrp_routing_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND(
            [[("id", "=", operation.ids)], safe_eval(action.domain or "[]")]
        )
        action_dict.update({"domain": domain})
        return action_dict


class MrpWorkcenterRoutingImportLine(models.Model):
    _name = "mrp.routing.workcenter.import.line"
    _inherit = "base.import.line"
    _description = "Lines to import workcenter routing"

    import_id = fields.Many2one(
        comodel_name="mrp.routing.workcenter.import",
        copy=False,
    )
    action = fields.Selection(
        selection_add=[
            ("create", "Create"),
        ],
        ondelete={"create": "set default"},
    )
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    bom_ref = fields.Char(
        states={"done": [("readonly", True)]},
        copy=False,
    )
    operation_name = fields.Char(
        states={"done": [("readonly", True)]},
        copy=False,
    )
    operation_id = fields.Many2one(
        comodel_name="mrp.routing.workcenter",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    workcenter_name = fields.Char(
        states={"done": [("readonly", True)]},
        copy=False,
    )
    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    product_code = fields.Char(
        states={"done": [("readonly", True)]},
        copy=False,
    )
    product_name = fields.Char(
        states={"done": [("readonly", True)]},
        copy=False,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        states={"done": [("readonly", True)]},
        copy=False,
    )

    def _action_validate(self):
        update_values = super()._action_validate()
        log_infos = []
        product = False
        bom, log_info_bom = self._check_bom()
        if log_info_bom:
            log_infos.append(log_info_bom)
        workcenter, log_info_workcenter = self._check_workcenter()
        if log_info_workcenter:
            log_infos.append(log_info_workcenter)
        if self.product_code or self.product_name:
            product, log_info_product = self._check_product()
            if log_info_product:
                log_infos.append(log_info_product)
        if product and bom:
            log_info_product_in_bom = self._check_product_in_bom(
                bom=bom, product=product
            )
            if log_info_product_in_bom:
                log_infos.append(log_info_product_in_bom)
        if not self.operation_name:
            log_infos.append(_("Error: Operation name is required."))
        state = "error" if log_infos else "pass"
        action = "create" if state != "error" else "nothing"
        update_values.update(
            {
                "bom_id": bom and bom.id,
                "workcenter_id": workcenter and workcenter.id,
                "product_id": product and product.id,
                "log_info": "\n".join(log_infos),
                "state": state,
                "action": action,
            }
        )
        return update_values

    def _action_process(self):
        update_values = super()._action_process()
        log_info = ""
        operation = False
        if self.action == "create" and self.state not in ("error", "done"):
            operation = self.operation_id
            if not operation:
                operation = self._create_operation()
            log_info = self._assign_operation_to_product(operation=operation)
            state = "error" if log_info else "done"
            update_values.update(
                {
                    "operation_id": operation and operation.id,
                    "state": state,
                    "log_info": log_info,
                }
            )
        return update_values

    def _check_bom(self):
        self.ensure_one()
        log_info = ""
        if self.bom_id:
            return self.bom_id, log_info
        bom_obj = self.env["mrp.bom"]
        if self.import_id.company_id:
            bom_obj = bom_obj.with_company(self.import_id.company_id)
        search_domain = [
            ("code", "=", self.bom_ref),
            ("company_id", "=", self.import_id.company_id.id),
        ]
        boms = bom_obj.search(search_domain)
        if not boms:
            boms = False
            log_info = _("Error: BoM not found.")
        elif len(boms) != 1:
            boms = False
            log_info = _("Error: More than one BoM found.")
        return boms, log_info

    def _check_workcenter(self):
        self.ensure_one()
        log_info = ""
        if self.workcenter_id:
            return self.workcenter_id, log_info
        workcenter_obj = self.env["mrp.workcenter"]
        if self.import_id.company_id:
            workcenter_obj = workcenter_obj.with_company(self.import_id.company_id)
        search_domain = [
            ("name", "=", self.workcenter_name),
            ("company_id", "=", self.import_id.company_id.id),
        ]
        workcenters = workcenter_obj.search(search_domain)
        if not workcenters:
            workcenters = False
            log_info = _("Error: Workcenter not found.")
        elif len(workcenters) != 1:
            workcenters = False
            log_info = _("Error: More than one workcenter found.")
        return workcenters, log_info

    def _check_product(self):
        self.ensure_one()
        log_info = ""
        if self.product_id:
            return self.product_id, log_info
        product_obj = self.env["product.product"]
        if self.import_id.company_id:
            product_obj = product_obj.with_company(self.import_id.company_id)
        search_domain = [("name", "=", self.product_name)]
        if self.product_code:
            search_domain = expression.AND(
                [[("default_code", "=", self.product_code)], search_domain]
            )
        if self.import_id.product_found_by_code:
            search_domain = [("default_code", "=", self.product_code)]
        products = product_obj.search(search_domain)
        if not products:
            products = False
            log_info = _("Error: Product not found.")
        elif len(products) != 1:
            products = False
            log_info = _("Error: More than one product found.")
        return products, log_info

    def _check_product_in_bom(self, bom=False, product=False):
        self.ensure_one()
        log_info = ""
        bom_line_products = bom.mapped("bom_line_ids.product_id")
        if product not in bom_line_products:
            log_info = _("Error: Product not in BoM.")
        bom_line_products = bom.bom_line_ids.filtered(
            lambda c: not c.operation_id
        ).mapped("product_id")
        if product not in bom_line_products:
            log_info = _("Error: No product in BoM without operation.")
        return log_info

    def _create_operation(self):
        self.ensure_one()
        operation_obj = self.env["mrp.routing.workcenter"]
        if self.import_id.company_id:
            operation_obj = operation_obj.with_company(self.import_id.company_id)
        operation = operation_obj.new(
            {
                "name": self.operation_name,
                "bom_id": self.bom_id.id,
                "workcenter_id": self.workcenter_id.id,
            }
        )
        for onchange_method in operation._onchange_methods["bom_id", "workcenter_id"]:
            onchange_method(operation)
        vals = operation._convert_to_write(operation._cache)
        operation = operation_obj.create(vals)
        return operation

    def _assign_operation_to_product(self, operation=False):
        self.ensure_one()
        log_info = ""
        if self.product_id and self.bom_id:
            log_info = self._check_product_in_bom(
                bom=self.bom_id, product=self.product_id
            )
            if not log_info and operation:
                bom_line_products = self.bom_id.bom_line_ids.filtered(
                    lambda c: not c.operation_id and c.product_id == self.product_id
                ).sorted(lambda c: c.sequence)
                if bom_line_products:
                    bom_line_products[:1].operation_id = operation.id
        return log_info
