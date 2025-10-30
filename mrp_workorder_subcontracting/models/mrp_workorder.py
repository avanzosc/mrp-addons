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

    def create_subcontract_purchase(self):
        PurchaseOrder = self.env["purchase.order"]
        PurchaseOrderLine = self.env["purchase.order.line"]
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
                }
            )

            product_variant = wo.service_product_id.product_variant_id

            uom = wo.service_product_id.uom_po_id or wo.service_product_id.uom_id

            qty = wo.production_id.product_qty

            seller = product_variant._select_seller(
                partner_id=wo.service_supplier_id,
                quantity=qty,
                date=purchase_order.date_order.date(),
                uom_id=uom,
            )
            price_unit = seller.price if seller else 0.0

            PurchaseOrderLine.create(
                {
                    "order_id": purchase_order.id,
                    "product_id": wo.service_product_id.product_variant_id.id,
                    "product_qty": wo.production_id.product_qty,
                    "name": f"{wo.production_id.name} - {wo.sequence or ''} - {wo.name}",
                    "workorder_id": wo.id,
                    "product_uom": uom.id,
                    "price_unit": price_unit,
                }
            )

            for charge in wo.service_product_id.subcontracting_charge_ids:
                qty_to_use = charge.compute_charge_qty(wo.production_id)

                PurchaseOrderLine.create(
                    {
                        "order_id": purchase_order.id,
                        "product_id": charge.product_id.product_variant_id.id,
                        "product_qty": qty_to_use,
                        "name": f"{charge.product_id.name} ({wo.name})",
                        "workorder_id": wo.id,
                    }
                )

            wo.purchase_id = purchase_order.id
