# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ServiceType(models.Model):
    _name = "service.type"

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")


class ProductCategory(models.Model):
    _inherit = "product.category"

    service_type = fields.Many2one(comodel_name="service.type")
