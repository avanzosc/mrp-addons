# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, fields, models


class MrpProductionHistorical(models.Model):
    _name = "mrp.production.historical"
    _description = "MRP Production historical"

    production_id = fields.Many2one(
        string="MRP Production", comodel_name="mrp.production", copy=False
    )
    production_bom_id = fields.Many2one(
        string="BoM",
        comodel_name="mrp.bom",
        store=True,
        copy=False,
        related="production_id.bom_id",
    )
    historical_date = fields.Datetime(string="Date", copy=False)
    user_id = fields.Many2one(string="User", comodel_name="res.users", copy=False)
    product_id = fields.Many2one(
        string="Product", comodel_name="product.product", copy=False
    )
    programed_qty = fields.Float(
        string="Programed quantity", digits="Product Unit of Measure", copy=False
    )
    scraped_qty = fields.Float(
        string="Scraped quantity", digits="Product Unit of Measure", copy=False
    )
    type = fields.Selection(
        string="Type",
        selection=[
            ("scraped", _("Scraped product")),
            ("add", _("Added product")),
            ("bomadd", _("BoM: Added product")),
            ("bomdel", _("BoM: Deleted product")),
            ("bommod", _("BoM: Modified line")),
        ],
    )
    bom_id = fields.Many2one(string="BoM", comodel_name="mrp.bom", copy=False)
    bom_line_movement = fields.Char(string="BoM line movement", copy=False)
    bom_line_changes = fields.Text(string="BoM line changes", copy=False)
