# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductionProductLabelWizard(models.TransientModel):
    _name = "production.product.label.wizard"
    _description = "Production Product Label Wizard"

    mrp_production_id = fields.Many2one(
        string="Orden de Producción", comodel_name="mrp.production", readonly=True
    )

    product_id = fields.Many2one(
        string="Product", comodel_name="product.product", readonly=True
    )
    production_product_label_line_ids = fields.One2many(
        string="Wizard Lines",
        comodel_name="production.product.label.wizard.line",
        inverse_name="wizard_id",
    )
    remaining_quantity = fields.Integer(
        string="Remaining units of the product", readonly=True, default=0
    )
    allowed_lot_ids = fields.Many2many(string="Lots", comodel_name="stock.lot")
    bin = fields.Char(size=20)

    @api.model
    def default_get(self, field_vals):
        res = super().default_get(field_vals)
        active_id = self.env.context.get("active_id")
        if active_id:
            production = self.env["mrp.production"].browse(active_id)
            res["mrp_production_id"] = production.id
            res["product_id"] = production.product_id.id
            res["remaining_quantity"] = production.product_qty
            lots = self.env["stock.lot"].search(
                [("product_id", "=", production.product_id.id)]
            )
            if lots:
                res["allowed_lot_ids"] = [(6, 0, lots.ids)]
        return res

    @api.onchange("production_product_label_line_ids")
    def onchange_production_product_label_line_ids(self):
        if not self.is_ok_product_qty():
            self.show_warning_message()
        qty = self.get_product_qty()
        self.remaining_quantity = self.mrp_production_id.product_qty - qty

    def print_product_label(self):
        if not self.is_ok_product_qty():
            self.show_warning_message()
        if not self.production_product_label_line_ids:
            raise ValidationError(_("You must enter a line to print the label."))
        action = self.env.ref(
            "mrp_qr_label.action_production_product_label_wizard_report"
        )
        return action.report_action(self)

    def is_ok_product_qty(self):
        qty = self.get_product_qty()
        return False if qty > self.mrp_production_id.product_qty else True

    def get_product_qty(self):
        qty = 0
        if self.production_product_label_line_ids:
            qty = sum(self.mapped("production_product_label_line_ids.product_qty"))
        return qty

    def show_warning_message(self):
        if not self.template_label_line_ids:
            raise ValidationError(
                _(
                    "You cannot indicate a larger quantity than the one existing"
                    " in the production order."
                )
            )


class ProductionProductLabelWizardLine(models.TransientModel):
    _name = "production.product.label.wizard.line"
    _description = "Production Product Label Wizard Line"

    wizard_id = fields.Many2one(
        string="Production Product Label Wizard",
        comodel_name="production.product.label.wizard",
    )
    lot_id = fields.Many2one(string="Lot", comodel_name="stock.lot")
    product_qty = fields.Integer(string="Quantity", default=0)
    qr_code = fields.Char(string="QR Code", compute="_compute_qr_code")

    def _compute_qr_code(self):
        for line in self:
            product = self.wizard_id.mrp_production_id.product_id
            qr_code = "{} {}".format(
                product.default_code if product.default_code else "",
                line.lot_id.name if line.lot_id.name else "",
            )
            line.qr_code = qr_code
