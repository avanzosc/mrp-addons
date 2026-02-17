from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    service_product_id = fields.Many2one(
        "product.template",
        string="Product service",
        related="operation_id.service_product_id",
        store=True,
        readonly=True,
    )

    service_product_supplier_id = fields.Many2one(
        "product.supplierinfo",
        string="Product Supplier",
        related="operation_id.service_product_supplier_id",
        store=True,
        readonly=True,
    )

    service_supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        related="operation_id.service_supplier_id",
        store=True,
        readonly=True,
    )

    purchase_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        readonly=True,
    )

    def button_start(self):
        res = super().button_start()
        subcontract_lines = self.filtered(
            lambda w: w.service_product_id.subcon_operations
        )
        if subcontract_lines:
            for wo in subcontract_lines:
                wo.create_subcontract_purchase()
        return res

    def _get_price(self, product, partner, qty, date_order):
        uom = product.uom_po_id or product.uom_id
        seller = product._select_seller(
            partner_id=partner,
            quantity=qty,
            date=date_order.date(),
            uom_id=uom,
        )
        return seller.price if seller else 0.0

    def _create_purchase_line(self, purchase_order, wo, product, type_charge=None):

        qty = self.env["product.subcontracting.charge"].compute_qty(
            wo.production_id, type_charge=type_charge
        )

        price_unit = self._get_price(
            product,
            wo.service_supplier_id,
            qty,
            purchase_order.date_order,
        )

        uom = product.uom_po_id or product.uom_id
        self.env["purchase.order.line"].create(
            {
                "order_id": purchase_order.id,
                "product_id": product.id,
                "product_qty": qty,
                "name": f"{wo.production_id.name} - {wo.sequence or ''} - {wo.name}",
                "workorder_id": wo.id,
                "product_uom": uom.id,
                "price_unit": price_unit,
            }
        )

    def create_subcontract_purchase(self):
        PurchaseOrder = self.env["purchase.order"]
        for wo in self:
            existing_po = PurchaseOrder.search(
                [
                    ("workorder_id", "=", wo.id),
                    ("partner_id", "=", wo.service_supplier_id.id),
                    ("state", "not in", ["cancel"]),
                ],
                limit=1,
            )

            if existing_po:
                wo.purchase_id = existing_po.id
                continue

            purchase_order = PurchaseOrder.with_context(
                mail_create_nosubscribe=True
            ).create(
                {
                    "partner_id": wo.service_supplier_id.id,
                    "origin": f"{wo.production_id.name} - {wo.sequence or ''} - {wo.name}",
                    "subcon_purchase": True,
                    "date_order": fields.Datetime.now(),
                    "workorder_id": wo.id,
                    "bom_id": (
                        wo.production_id.bom_id.id if wo.production_id.bom_id else False
                    ),
                }
            )

            product_variant = wo.service_product_id.product_variant_id

            self._create_purchase_line(
                purchase_order, wo, product_variant, type_charge="standard"
            )

            for charge in wo.service_product_id.subcontracting_charge_ids:

                product_variant_charge = charge.product_id.product_variant_id
                type_charge = charge.quantity_calculation
                self._create_purchase_line(
                    purchase_order, wo, product_variant_charge, type_charge=type_charge
                )

            wo.purchase_id = purchase_order.id
