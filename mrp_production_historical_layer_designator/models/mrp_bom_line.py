# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def _verify_changes_to_historical(self, vals):
        changes_found = super()._verify_changes_to_historical(vals)
        if "layer" in vals or "designator" in vals:
            changes_found = True
        return changes_found

    def _generate_literals_for_historical(self, vals):
        text = super()._generate_literals_for_historical(vals)
        if "layer" in vals:
            text = _(
                "%(text)s\n* Replaced the layer: %(old_layer)s, by the "
                "new layer: %(new_layer)s"
            ) % {
                "text": text,
                "old_layer": self.layer,
                "new_layer": vals.get("layer"),
            }
        if "designator" in vals:
            text = _(
                "%(text)s\n* Replaced the designator: %(old_desig)s, by the "
                "new designator: %(new_desig)s"
            ) % {
                "text": text,
                "old_desig": self.designator,
                "new_desig": vals.get("designator"),
            }
        return text
