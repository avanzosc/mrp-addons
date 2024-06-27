# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class QcTestMethod(models.Model):
    _name = "qc.test.method"
    _description = "Method used to do the test"

    name = fields.Char(string="Method Name")
