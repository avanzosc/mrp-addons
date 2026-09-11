# Copyright 2026 Inael
# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.osv.expression import AND


class MrpLaserCutOrderLine(models.Model):
    _name = "mrp.laser.cut.order.line"
    _description = "Laser Cutting Order Distribution Line"
    _order = "order_id, id"
    _rec_name = "product_id"

    order_id = fields.Many2one(
        comodel_name="mrp.laser.cut.order",
        string="Laser Cutting Order",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        domain=[("is_laser_cut", "=", True)],
        help="Finished product cut from the raw material on this layout.",
    )
    unit_consumption = fields.Float(
        string="Consumption",
        compute="_compute_unit_consumption",
        store=True,
        readonly=False,
        help="Raw material one unit of this product consumes, in the unit of "
        "measure of the raw material, taken from the raw material line of the "
        "product's Bill of Materials. It can be overridden to account for the "
        "cutting loss.",
    )
    output_per_unit = fields.Float(
        string="Output",
        help="How many units of this product are cut from a single unit of "
        "raw material on this layout. Entered by hand from the nesting.",
    )
    line_consumption = fields.Float(
        compute="_compute_line_consumption",
        store=True,
        help="Consumption multiplied by Output: the raw material this "
        "product takes out of a single unit of raw material.",
    )
    output_qty = fields.Float(
        string="Total Output",
        compute="_compute_output_qty",
        store=True,
        help="Quantity of the order multiplied by Output: the total quantity "
        "of this product produced.",
    )
    drawing_ref = fields.Char(
        string="Drawing",
        help="Reference of the part drawing cut on this line.",
    )

    @api.depends("output_per_unit", "order_id.material_qty")
    def _compute_output_qty(self):
        for line in self:
            line.output_qty = line.order_id.material_qty * line.output_per_unit

    @api.depends("product_id", "order_id.raw_material_id")
    def _compute_unit_consumption(self):
        for line in self:
            line.unit_consumption = (
                line._get_unit_consumption(
                    line.product_id, line.order_id.raw_material_id
                )
                or line.product_id.weight
            )

    @api.depends("unit_consumption", "output_per_unit")
    def _compute_line_consumption(self):
        for line in self:
            line.line_consumption = line.unit_consumption * line.output_per_unit

    @api.model
    def _get_bom(self, product, material):
        bom_model = self.env["mrp.bom"]
        if not product or not material:
            return bom_model
        domain = AND(
            [
                bom_model._bom_find_domain(product, company_id=self.env.company.id),
                [("bom_line_ids.product_id", "=", material.id)],
            ]
        )
        return bom_model.search(domain, order="sequence, product_id, id", limit=1)

    @api.model
    def _get_unit_consumption(self, product, material):
        bom = self._get_bom(product, material)
        if not bom or not bom.product_qty:
            return 0
        bom_line = bom.bom_line_ids.filtered(lambda line: line.product_id == material)[
            :1
        ]
        return bom_line.product_qty / bom.product_qty

    @api.onchange("product_id")
    def _onchange_product_id(self):
        material = self.order_id.raw_material_id
        if not self.product_id or not material:
            return
        self.unit_consumption = (
            self._get_unit_consumption(self.product_id, material)
            or self.product_id.weight
        )
