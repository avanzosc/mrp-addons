# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpBomChange(models.Model):
    _name = "mrp.bom.change"
    _description = "Mrp BoM Component Change"

    @api.depends("old_component_id")
    def _compute_bom_ids(self):
        bom_obj = self.env["mrp.bom"]
        for change in self:
            boms = bom_obj
            change.bom_ids = [(6, 0, [])]
            if change.old_component_id:
                for bom in bom_obj.search([]):
                    bom_lines = bom.bom_line_ids.filtered(
                        lambda x: x.product_id.id == self.old_component_id.id
                    )
                    if bom_lines and bom not in boms:
                        boms += bom
            change.bom_ids = [(6, 0, boms.ids)]

    name = fields.Char(required=True, copy=False)
    new_component_id = fields.Many2one(
        string="New Component", comodel_name="product.product", required=True
    )
    old_component_id = fields.Many2one(
        string="Old Component", comodel_name="product.product", required=True
    )
    bom_ids = fields.Many2many(
        string="BoMs",
        comodel_name="mrp.bom",
        relation="rel_mrp_bom_change",
        column1="bom_change_id",
        column2="bom_id",
        copy=False,
        store=True,
        readonly=True,
        compute="_compute_bom_ids",
    )
    date = fields.Date(string="Change Date", readonly=True)
    user = fields.Many2one(string="Changed By", comodel_name="res.users", readonly=True)
    reason = fields.Char()

    def do_component_change(self):
        self.ensure_one()
        if not self.old_component_id or not self.new_component_id:
            raise ValidationError(_("Not Components selected!"))
        if not self.bom_ids:
            raise ValidationError(_("There isn't any BoM for selected component"))
        for bom in self.bom_ids:
            bom_lines = bom.bom_line_ids.filtered(
                lambda x: x.product_id.id == self.old_component_id.id
            )
            values, bom_lines = self._get_new_component(bom_lines)
            # add product_tmpl_id in case of mrp_product_variants are installed
            if hasattr(bom_lines, "product_tmpl_id"):
                values["product_tmpl_id"] = self.new_component_id.product_tmpl_id.id
            bom_lines.write(values)
        self.write({"date": fields.Date.context_today(self), "user": self.env.user.id})
        return {
            "name": _("Bill of Material"),
            "view_mode": "tree,form",
            "res_model": "mrp.bom",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.bom_ids.mapped("id"))],
        }

    def _get_new_component(self, bom_lines):
        values = {"product_id": self.new_component_id.id}
        return values, bom_lines
