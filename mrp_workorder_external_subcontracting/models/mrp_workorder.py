from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    service_product_id = fields.Many2one(
        comodel_name="product.template",
        string="Service Product",
        related="operation_id.service_product_id",
        store=True,
        readonly=True,
    )
    service_product_supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Product Supplier",
        related="operation_id.service_product_supplier_id",
        store=True,
        readonly=True,
    )
    service_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        related="operation_id.service_supplier_id",
        store=True,
        readonly=True,
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
        readonly=True,
        copy=False,
    )
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials",
        related="production_id.bom_id",
        store=True,
        readonly=True,
    )

    def button_start(self, *args, **kwargs):
        result = super().button_start(*args, **kwargs)
        self.filtered(
            "service_product_id.subcon_operations"
        )._create_subcontract_purchase()
        return result

    def _get_subcontract_price(self, product, partner, quantity, date_order):
        purchase_uom = product.uom_po_id or product.uom_id
        seller = product._select_seller(
            partner_id=partner,
            quantity=quantity,
            date=date_order.date(),
            uom_id=purchase_uom,
        )
        return seller.price if seller else 0.0

    def _create_subcontract_purchase_line(
        self, purchase_order, product, type_charge=None
    ):
        self.ensure_one()
        quantity = self.env["product.subcontracting.charge"].compute_qty(
            self.production_id,
            type_charge=type_charge,
        )
        purchase_uom = product.uom_po_id or product.uom_id
        self.env["purchase.order.line"].create(
            {
                "order_id": purchase_order.id,
                "product_id": product.id,
                "product_qty": quantity,
                "name": self._get_subcontract_origin(),
                "workorder_id": self.id,
                "product_uom": purchase_uom.id,
                "price_unit": self._get_subcontract_price(
                    product,
                    self.service_supplier_id,
                    quantity,
                    purchase_order.date_order,
                ),
            }
        )

    def _get_subcontract_origin(self):
        self.ensure_one()
        return f"{self.production_id.name} - {self.sequence or ''} - {self.name}"

    def _create_subcontract_purchase(self):
        purchase_order_model = self.env["purchase.order"]
        for workorder in self:
            purchase_order = purchase_order_model.search(
                [
                    ("workorder_id", "=", workorder.id),
                    ("partner_id", "=", workorder.service_supplier_id.id),
                    ("state", "!=", "cancel"),
                ],
                limit=1,
            )
            if purchase_order:
                workorder.purchase_id = purchase_order
                continue

            purchase_order = purchase_order_model.with_context(
                mail_create_nosubscribe=True
            ).create(
                {
                    "partner_id": workorder.service_supplier_id.id,
                    "origin": workorder._get_subcontract_origin(),
                    "subcon_purchase": True,
                    "date_order": fields.Datetime.now(),
                    "workorder_id": workorder.id,
                    "bom_id": workorder.bom_id.id,
                }
            )
            workorder._create_subcontract_purchase_line(
                purchase_order,
                workorder.service_product_id.product_variant_id,
                type_charge="standard",
            )
            for charge in workorder.service_product_id.subcontracting_charge_ids:
                workorder._create_subcontract_purchase_line(
                    purchase_order,
                    charge.product_id.product_variant_id,
                    type_charge=charge.quantity_calculation,
                )
            workorder.purchase_id = purchase_order
