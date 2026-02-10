# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class QcTestLabel(models.Model):
    _name = "qc.test.label"
    _description = "Quanlity Control Test Labels"
    _order = "name"

    name = fields.Char(string="name")
