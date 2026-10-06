# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CleaningDatabaseWarningWizard(models.TransientModel):
    _inherit = "cleaning.database.warning.wizard"

    object_to_delete = fields.Selection(
        selection_add=[
            ("mrp", "MRP"),
        ],
        ondelete={"mrp": "cascade"},
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        if self.env.context.get("default_object_to_delete") == "mrp":
            res["text"] = _(
                "You are about to delete manufacturing operations for "
                "the selected companies.\n\n"
                "MRP Work Orders will be deleted first, followed by "
                "Manufacturing Orders.\n\n"
                "This operation is irreversible."
            )

        return res

    def continue_with_cleaning_database(self):
        self.ensure_one()

        if self.object_to_delete == "mrp":
            cleaning_database = (
                self.env["cleaning.database"]
                .browse(self.env.context.get("active_id"))
                .exists()
            )

            if not cleaning_database:
                raise UserError(_("Cleaning Database record not found."))

            return cleaning_database.action_delete_mrp_operations()

        return super().continue_with_cleaning_database()
