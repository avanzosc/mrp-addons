# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _copy_bom(self):
        new_bom = super()._copy_bom()
        new_bom._create_version_activate_historical("version")
        return new_bom

    def button_activate(self):
        result = super().button_activate()
        for bom in self:
            bom._create_version_activate_historical("activated")
        return result

    def _create_version_activate_historical(self, text):
        production_obj = self.env["mrp.production"]
        historical_obj = self.env["mrp.production.historical"]
        if text == "version":
            my_text = _("It has been changed to version {}.").format(self.version)
        else:
            my_text = _("The BoM with version {}, has been activated.").format(
                self.version
            )
        vals = {
            "bom_id": self.id,
            "historical_date": fields.Datetime.now(),
            "user_id": self.env.user.id,
            "type": "bommod",
            "bom_line_changes": my_text,
        }
        historical_obj.create(vals)
        vals.pop("bom_id")
        cond = [
            ("product_tmpl_id", "=", self.product_tmpl_id.id),
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]
        if self.product_id:
            cond.append(("product_id", "=", self.product_id.id))
        boms = self.search(cond)
        cond = [
            ("bom_id", "in", boms.ids),
            ("state", "not in", ("done", "cancel", "draft")),
        ]
        productions = production_obj.search(cond)
        for production in productions:
            vals["production_id"] = production.id
            historical_obj.with_context(from_bom_activated=True).create(vals)
