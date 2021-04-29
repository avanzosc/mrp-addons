# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, exceptions


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.constrains('bom_line_ids')
    def _check_one_main_material(self):
        for record in self:
            if len(record.bom_line_ids.filtered(lambda x: x.main_material)) \
                    > 1:
                raise exceptions.ValidationError(
                    "There can only be one main material")


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    main_material = fields.Boolean(string="Main Material")

    @api.constrains("operation_id", "main_material")
    def _check_main_material_operation(self):
        for record in self:
            if record.main_material and not record.operation_id:
                raise exceptions.ValidationError(
                    "Main material must have an operation")
