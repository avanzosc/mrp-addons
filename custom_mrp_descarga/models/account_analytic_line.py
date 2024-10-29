# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    production_id = fields.Many2one(string="Production", comodel_name="mrp.production")
    mrp_production_id = fields.Many2one(
        string="Production Order",
        comodel_name="mrp.production",
    )
    unload_date = fields.Datetime(
        string="Unload Date",
        related="production_id.saca_line_id.unload_date",
        store=True,
    )
    task_name = fields.Char(
        related="task_id.name",
        store=True,
    )
    descarga_order = fields.Char(
        related="mrp_production_id.descarga_order",
        store=True,
    )
    breeding_id = fields.Many2one(
        comodel_name="stock.picking.batch",
        related="mrp_production_id.breeding_id",
        store=True,
    )
    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        related="mrp_production_id.vehicle_id",
        store=True,
    )
    remolque_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        related="mrp_production_id.remolque_id",
        store=True,
    )
    production_product_id = fields.Many2one(
        comodel_name="product.product",
        related="mrp_production_id.product_id",
        store=True,
    )
    lot_producing_id = fields.Many2one(
        comodel_name="stock.production.lot",
        related="mrp_production_id.lot_producing_id",
        store=True,
    )
    average_weight = fields.Float(
        related="mrp_production_id.average_weight",
        store=True,
    )
    download_unit = fields.Integer(
        related="mrp_production_id.download_unit",
        store=True,
    )
    origin_qty = fields.Float(
        related="mrp_production_id.origin_qty",
        store=True,
    )
    production_product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="mrp_production_id.product_uom_id",
        store=True,
    )
    rto_percentage = fields.Float(
        related="mrp_production_id.rto_percentage",
        store=True,
    )
    purchase_unit_price = fields.Float(
        related="mrp_production_id.purchase_unit_price",
        store=True,
    )
    asphyxiation_units = fields.Integer(
        related="mrp_production_id.asphyxiation_units",
        store=True,
    )
    seized_units = fields.Integer(
        related="mrp_production_id.seized_units",
        store=True,
    )
    purchase_price = fields.Float(
        related="mrp_production_id.purchase_price",
        store=True,
    )
    cost = fields.Float(
        related="mrp_production_id.cost",
        store=True,
    )
    entry_total_amount = fields.Float(
        related="mrp_production_id.entry_total_amount",
        store=True,
    )
    dif_total_amount = fields.Float(
        related="mrp_production_id.dif_total_amount",
        store=True,
    )
    production_state = fields.Selection(
        related="mrp_production_id.state",
        store=True,
    )
