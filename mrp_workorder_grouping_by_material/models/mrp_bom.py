# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, exceptions, _


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.constrains('bom_line_ids')
    def _check_one_main_material(self):
        for record in self:
            operations = []
            for line in record.bom_line_ids.filtered(
                    lambda x: x.main_material):
                operation_id = line.operation_id.id
                if operation_id not in operations:
                    operations.append(operation_id)
                else:
                    raise exceptions.ValidationError(_(
                        "There can only be one main material per operation. "
                        "Check lines that contains operation: {}").format(
                            line.operation_id.name))


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    main_material = fields.Boolean(string="Main Material")

    @api.constrains("operation_id", "main_material")
    def _check_main_material_operation(self):
        for record in self:
            if record.main_material and not record.operation_id:
                raise exceptions.ValidationError(_(
                    "Main material must have an operation"))
