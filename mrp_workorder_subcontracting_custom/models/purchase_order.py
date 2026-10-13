from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    subcon_purchase = fields.Boolean(string="suncontracting purchase", default=False)

    workorder_id = fields.Many2one("mrp.workorder", string="Work Order")

    production_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Order",
        related="workorder_id.production_id",
        store=True,
        readonly=True,
    )

    bom_id = fields.Many2one("mrp.bom", string="Lista de materiales")

    def _inter_company_create_sale_order(self, dest_company):
        self.ensure_one()

        sale_order = super()._inter_company_create_sale_order(dest_company)

        if self.bom_id and sale_order:
            sale_order.write({"bom_id": self.bom_id.id})

        return sale_order
