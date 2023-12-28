# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(MrpBom, self).onchange_product_id()
        if self.product_id:
            for line in self.operation_ids:
                line.bom_product_template_attribute_value_ids = False
        return result

    @api.constrains('product_id', 'product_tmpl_id', 'operation_ids')
    def _check_bom_lines(self):
        result = super(MrpBom, self)._check_bom_lines()
        for bom in self:
            for operation in bom.operation_ids:
                if bom.product_id and operation.bom_product_template_attribute_value_ids:
                    raise ValidationError(_("BoM cannot concern product %s and have a line with attributes (%s) at the same time.")
                        % (bom.product_id.display_name, ", ".join([ptav.display_name for ptav in operation.bom_product_template_attribute_value_ids])))
                for ptav in operation.bom_product_template_attribute_value_ids:
                    if ptav.product_tmpl_id != bom.product_tmpl_id:
                        raise ValidationError(_(
                            "The attribute value %(attribute)s set on product %(product)s does not match the BoM product %(bom_product)s.",
                            attribute=ptav.display_name,
                            product=ptav.product_tmpl_id.display_name,
                            bom_product=operation.parent_product_tmpl_id.display_name
                        ))
        return result
