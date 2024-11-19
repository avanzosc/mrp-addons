# Copyright 2024 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class CleaningDatabase(models.Model):
    _inherit = "cleaning.database"

    def action_delete_mrp_operations(self):
        self.env.cr.execute(
            "DELETE FROM mrp_workorder "
            "WHERE production_id in (select p.id "
            "                        from mrp_production as p "
            "                        where p.id = mrp_workorder.production_id "
            "                          and p.company_id in %s)",
            [tuple(self.company_ids.ids)],
        )
        self.env.cr.execute(
            "DELETE FROM mrp_production WHERE company_id in %s",
            [tuple(self.company_ids.ids)],
        )
