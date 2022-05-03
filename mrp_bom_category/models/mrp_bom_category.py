# Copyright 2022 Gonzalo Nuin - AvanzOSC
# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
        

class MrpBomCategory(models.Model):
    _name = "mrp.bom.category"
    _description = "MRP BoM Category"

    name = fields.Char(
        string="Name",
        required=True,
    )

    _sql_constraints = [
        ("name_unique", "unique(name)", "Category name already exists"),
    ]
