from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    service_product_id = fields.Many2one(
        comodel_name="product.template",
        string="Service Product",
    )
    workcenter_is_external = fields.Boolean(
        related="workcenter_id.is_external",
        string="External",
    )
    service_product_supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Product Supplier",
    )
    service_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        related="service_product_supplier_id.partner_id",
        store=True,
        readonly=True,
    )

    @api.onchange("service_product_id")
    def _onchange_service_product_id(self):
        for operation in self:
            operation.service_product_supplier_id = self.env[
                "product.supplierinfo"
            ].search(
                [("product_tmpl_id", "=", operation.service_product_id.id)],
                order="sequence, id",
                limit=1,
            )
