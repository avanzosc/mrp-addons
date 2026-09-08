# Copyright 2026 Inael
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class OrderOlaserLista(models.Model):
    _name = "order.olaser.lista"
    _description = "Laser Cutting Order Distribution Line"

    olaser_id = fields.Many2one(
        comodel_name="order.olaser",
        string="Laser Order",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        domain=[("is_laser_cut", "=", True)],
    )
    cantidad_consumo = fields.Float(
        string="Kg per BOM Unit",
        help="Quantity of raw material needed to produce one unit of this "
        "product, according to its own Bill of Materials.",
    )
    cantidad_chapa = fields.Float(
        string="Units per Sheet",
        help="How many units of this product are produced from one sheet.",
    )
    cantidad_consumo_total = fields.Float(
        string="Line Weight (kg)",
        compute="_compute_cantidad_consumo_total",
        store=True,
        help="Kg per BOM Unit * Units per Sheet.",
    )
    cantidad_chapa_total = fields.Float(
        string="Total Quantity",
        compute="_compute_cantidad_chapa_total",
        store=True,
        help="Quantity of the laser cutting order * Units per Sheet.",
    )
    plano = fields.Char(string="Drawing Number")
    cantidad_chapa_termi = fields.Float(
        string="Reported Units",
        help="Legacy field from the workflow prior to native manufacturing "
        "orders; not used by new orders.",
    )
    tiempo_ud = fields.Float(
        string="Time per Unit",
        help="Legacy field from the workflow prior to native manufacturing "
        "orders; not used by new orders.",
    )
    tiempo_total = fields.Float(
        string="Total Time",
        help="Legacy field from the workflow prior to native manufacturing "
        "orders; not used by new orders.",
    )
    peso_gas = fields.Float(
        string="Gas Weight",
        help="Legacy field from the workflow prior to native manufacturing "
        "orders; not used by new orders.",
    )
    peso_gas_total = fields.Float(
        string="Total Gas Weight",
        help="Legacy field from the workflow prior to native manufacturing "
        "orders; not used by new orders.",
    )

    @api.depends("cantidad_consumo", "cantidad_chapa")
    def _compute_cantidad_consumo_total(self):
        for line in self:
            line.cantidad_consumo_total = line.cantidad_consumo * line.cantidad_chapa

    @api.depends("olaser_id.cantidad", "cantidad_chapa")
    def _compute_cantidad_chapa_total(self):
        for line in self:
            line.cantidad_chapa_total = line.olaser_id.cantidad * line.cantidad_chapa

    @api.model
    def _get_bom_qty(self, product, material):
        """Kg of ``material`` needed to produce one unit of ``product``,
        according to ``product``'s own Bill of Materials."""
        if not product or not material:
            return 0
        bom = self.env["mrp.bom"]._bom_find(product)[product]
        if not bom or not bom.product_qty:
            return 0
        bom_line = bom.bom_line_ids.filtered(lambda line: line.product_id == material)[
            :1
        ]
        return bom_line.product_qty / bom.product_qty

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.cantidad_consumo = self._get_bom_qty(
            self.product_id, self.olaser_id.product_id
        )
