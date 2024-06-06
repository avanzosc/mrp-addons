# -*- coding: utf-8 -*-
# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBomChange(models.Model):
    _inherit = "mrp.bom.change"

    create_new_version = fields.Boolean(
        string="Create new BoM version", help="Check this field if you want to"
        " create a new version of the BOM before modifying the component"
    )

    def _get_new_component(self, bom_lines):
        if self.create_new_version:
            new_bom = bom_lines[0].bom_id._copy_bom()
            bom_lines[0].bom_id.button_historical()
            new_bom.button_activate()
            self.bom_ids = [(3, bom_lines[0].bom_id.id)]
            self.bom_ids = [(4, new_bom.id)]
            bom_lines = new_bom.bom_line_ids.filtered(
                lambda x: x.product_id.id == self.old_component_id.id)
        return super(MrpBomChange, self)._get_new_component(bom_lines)
