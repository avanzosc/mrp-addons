# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class BizerbaImportLine(models.Model):
    _name = "bizerba.import.line"
    _inherit = "base.import.line"
    _description = "Wizard lines to import Bizerba lines"

    production_id = fields.Many2one(string="Production", comodel_name="mrp.production")
    action = fields.Selection(
        string="Action",
        selection=[
            ("create", "Create"),
            ("nothing", "Nothing"),
        ],
        default="nothing",
        states={"done": [("readonly", True)]},
        copy=False,
        required=True,
    )
    line_product_code = fields.Char(
        string="Product Code",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    line_product_qty = fields.Float(
        string="Product Qty",
        states={"done": [("readonly", True)]},
        copy=False,
        digits="Bizerba Product Qty Decimal Precision",
    )
    line_uom = fields.Char(
        string="UoM",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    line_chicken_code = fields.Char(
        string="Chicken Code",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    line_date = fields.Datetime(
        string="Date",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    line_product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    line_uom_id = fields.Many2one(
        string="UoM",
        comodel_name="uom.uom",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    line_lot = fields.Char(
        string="Lot",
        states={"done": [("readonly", True)]},
        copy=False,
    )

    def _action_validate(self):
        update_values = super()._action_validate()
        self.production_id.action_confirm()
        log_infos = []
        product, log_info_product = self._check_product()
        if log_info_product:
            log_infos.append(log_info_product)
        uom, log_info_uom = self._check_uom()
        if log_info_uom:
            log_infos.append(log_info_uom)
        state = "error" if log_infos else "pass"
        action = "nothing"
        if state != "error":
            action = "create"
        update_values.update({
            "line_uom_id": uom and uom.id,
            "line_product_id": product and product.id,
            "log_info": "\n".join(log_infos),
            "state": state,
            "action": action,
        })
        return update_values

    def _action_process(self):
        update_values = super()._action_process()
        if self.action == "create":
            log_info = ""
            move_line = self.production_id.move_line_ids.filtered(
                    lambda c: c.product_id == self.line_product_id
                )
            if move_line:
                move_line[:1].write(
                        {
                            "container": move_line[:1].container + 1,
                            "qty_done": move_line[:1].qty_done + self.line_product_qty,
                            "product_uom_id": self.line_uom_id.id,
                        }
                    )
                move_line[:1].onchange_container()
                move_line[:1].onchange_unit()
            else:
                log_info = _("Error: There is no entry line with this product.")
            state = "error" if log_info else "done"
            action = "nothing"
            update_values.update({
                "log_info": log_info,
                "action": action,
                "state": state
            })
        return update_values

    def _check_product(self):
        self.ensure_one()
        log_info = ""
        if self.line_product_id:
            return self.line_product_id, log_info
        product_obj = self.env["product.product"]
        if self.line_product_code:
            code = self.line_product_code
        else:
            code = self.line_chicken_code
        search_domain = [("bizerba_code", "=", code)]
        products = product_obj.search(search_domain)
        if not products:
            products = False
            log_info = _("Error: No product found.")
        elif len(products) > 1:
            products = False
            log_info = _(
                "Error: More than one product with Bizerba code {} found."
            ).format(code)
        elif len(products) == 1:
            if not self.production_id.move_line_ids.filtered(
                lambda c: c.product_id == products
            ):
                log_info = _("Error: There is no entry line with this product.")
        return products and products[:1], log_info

    def _check_uom(self):
        self.ensure_one()
        log_info = ""
        if self.line_uom_id:
            return self.line_uom_id, log_info
        uom_obj = self.env["uom.uom"]
        search_domain = [("name", "=ilike", self.line_uom)]
        uoms = uom_obj.search(search_domain)
        if not uoms:
            uoms = False
            log_info = _("Error: No UoM found.")
        elif len(uoms) > 1:
            uoms = False
            log_info = _("Error: More than one UoM with name {} found.").format(
                self.line_uom
            )
        return uoms and uoms[:1], log_info
