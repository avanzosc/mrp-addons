# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    @api.model_create_multi
    def create(self, vals):
        lines = super().create(vals)
        if "no_create_historical" not in self.env.context:
            for line in lines:
                line._create_production_historical("add")
        return lines

    def unlink(self):
        for line in self:
            line._create_production_historical("delete")
        return super().unlink()

    def write(self, vals):
        if "no_create_historical" not in self.env.context:
            if "product_uom_qty" in vals:
                vals["load_cost"] = bool(vals.get("product_uom_qty", 0.0))
            changes_found = self._verify_changes_to_historical(vals)
            if changes_found:
                for line in self:
                    text = line._generate_literals_for_historical(vals)
                    line._create_production_historical("update", text=text)
        return super().write(vals)

    def _verify_changes_to_historical(self, vals):
        changes_found = False
        if (
            "product_id" in vals
            or "product_qty" in vals
            or "product_uom" in vals
            or "manufacturer_code" in vals
        ):
            changes_found = True
        return changes_found

    def _generate_literals_for_historical(self, vals):
        text = _(
            "The product: %(product)s the following changes have " "been made:"
        ) % {
            "product": self.product_id.name,
        }
        if "product_id" in vals:
            product = self.env["product.product"].browse(vals.get("product_id"))
            text = _("%(text)s\n* New product: %(product)s.") % {
                "text": text,
                "product": product.name,
            }
        if "product_qty" in vals:
            text = _(
                "%(text)s\n* Replaced the quantity: %(old_qty)s, by the new "
                "quantity: %(new_qty)s."
            ) % {
                "text": text,
                "old_qty": self.product_qty,
                "new_qty": vals.get("product_qty"),
            }
        if "product_uom" in vals:
            uom = self.env["product.uom"].browse(vals.get("product_uom"))
            text = _(
                "%(text)s\n* Replaced the unit of measure: %(old_unit)s, by "
                "the new measure: %(new_unit)s"
            ) % {
                "text": text,
                "old_unit": self.product_uom.name,
                "new_unit": uom.name,
            }
        if "manufacturer_code" in vals:
            text = _(
                "%(text)s\n* Replaced the manufacturer code: %(old_code)s, by "
                "the new manufacturer code: %(new_code)s"
            ) % {
                "text": text,
                "old_code": self.manufacturer_code,
                "new_code": vals.get("manufacturer_code"),
            }
        return text

    def _create_production_historical(self, my_type, text=False):
        production_obj = self.env["mrp.production"]
        historical_obj = self.env["mrp.production.historical"]
        vals = self._get_vals_production_historical(my_type, text=text)
        if my_type == "add":
            vals["bom_line_changes"] = _("Added BoM line")
        if my_type == "delete":
            vals["bom_line_changes"] = _("Deleted BoM line")
        vals["bom_id"] = self.bom_id.id
        historical_obj.create(vals)
        cond = [
            ("product_tmpl_id", "=", self.bom_id.product_tmpl_id.id),
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]
        if self.bom_id.product_id:
            cond.append(("product_id", "=", self.bom_id.product_id.id))
        boms = self.env["mrp.bom"].search(cond)
        cond = [
            ("bom_id", "in", boms.ids),
            ("state", "not in", ("done", "cancel", "draft")),
        ]
        productions = production_obj.search(cond)
        for production in productions:
            vals = self._get_vals_production_historical(my_type, text=text)
            vals["production_id"] = production.id
            if my_type == "update":
                historical_obj.with_context(bomline_historical_update=True).create(vals)
            else:
                historical_obj.with_context(bomline_historical_noupdate=True).create(
                    vals
                )

    def _get_vals_production_historical(self, my_type, text):
        vals = {
            "historical_date": fields.Datetime.now(),
            "user_id": self.env.user.id,
            "product_id": self.product_id.id,
            "programed_qty": self.product_qty,
        }
        if my_type == "add":
            vals.update({"type": "bomadd", "bom_line_movement": _("added")})
        elif my_type == "delete":
            vals.update({"type": "bomdel", "bom_line_movement": _("deleted")})
        else:
            vals.pop("programed_qty")
            vals.update({"type": "bommod", "bom_line_changes": text})
        return vals
