# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mrp_production_warn = fields.Selection(
        string="Manufacturing Order", related="product_id.mrp_production_warn"
    )
    mrp_production_warn_msg = fields.Text(
        string="Message for Manufacturing Order",
        related="product_id.mrp_production_warn_msg",
    )

    @api.onchange("product_id", "move_raw_ids")
    def _onchange_product_id(self):
        warning = {}
        title = False
        message = False
        if self.product_id and self.product_id.mrp_production_warn != "no-message":
            title = _("Warning for %s") % self.product_id.name
            message = self.product_id.mrp_production_warn_msg
            warning["title"] = title
            warning["message"] = message
            if self.product_id.mrp_production_warn == "block":
                return {
                    "value": {
                        "product_id": False,
                        "bom_id": False,
                        "product_uom_id": False,
                        "product_uom_qty": 0,
                    },
                    "warning": warning,
                }
        result = super()._onchange_product_id()
        if result and "warning" in result and result.get("warning", False):
            warning["title"] = (
                title
                and title + " & " + result["warning"]["title"]
                or result["warning"]["title"]
            )
            warning["message"] = (
                message
                and message + "\n\n" + result["warning"]["message"]
                or result["warning"]["message"]
            )
        if warning:
            if result is None:
                result = {}
            result["warning"] = warning
        return result
