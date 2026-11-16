# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_see_attachments(self):
        domain = [
            "|",
            "&",
            ("res_model", "=", "product.product"),
            ("res_id", "=", self.product_id.id),
            "&",
            ("res_model", "=", "product.template"),
            ("res_id", "=", self.product_id.product_tmpl_id.id),
        ]

        return {
            "name": _("Attachments"),
            "domain": domain,
            "res_model": "ir.attachment",
            "type": "ir.actions.act_window",
            "views": [(False, "kanban"), (False, "form")],
            "view_mode": "kanban,tree,form",
            "view_type": "form",
            "help": _(
                """<p class="oe_view_nocontent_create">
                            Click to upload files to your product.
                        </p><p>
                            Use this feature to store any files, like drawings
                            or specifications.
                        </p>"""
            ),
            "limit": 80,
            "context": "{'default_res_model': '%s','default_res_id': %d}"
            % ("product.product", self.product_id.id),
        }
