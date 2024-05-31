# Copyright 2024 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.bom.line"

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        related="bom_id.company_id",
        related_sudo=True,
        store=True,
    )
