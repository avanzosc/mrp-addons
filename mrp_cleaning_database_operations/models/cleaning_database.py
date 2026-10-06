# Copyright 2024 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models

from odoo.addons.cleaning_database_operations.models.cleaning_database import (
    CLEANUP_TABLE_LABELS,
)

CLEANUP_TABLE_LABELS.update(
    {
        "mrp_workorder": "MRP Work Orders",
        "mrp_production": "Manufacturing Orders",
    }
)


class CleaningDatabase(models.Model):
    _inherit = "cleaning.database"

    def _delete_all_operations(self):
        result = super()._delete_all_operations()
        self._delete_mrp_operations()
        return result

    def _delete_mrp_operations(self):
        self.ensure_one()

        if self._is_full_database_cleanup():
            self._delete_in_batches(
                table="mrp_workorder",
                where_clause="TRUE",
                params=(),
            )
        else:
            self._delete_in_batches(
                table="mrp_workorder",
                where_clause="""
                    production_id IN (
                        SELECT id
                        FROM mrp_production
                        WHERE company_id = ANY(%s)
                    )
                """,
                params=(self.company_ids.ids,),
            )

        self._delete_company_table("mrp_production")

    def action_delete_mrp_operations(self):
        self.ensure_one()

        self._delete_mrp_operations()
        self.env.invalidate_all()

        return True
