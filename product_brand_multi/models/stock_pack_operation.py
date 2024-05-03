# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import api, fields, models


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    @api.multi
    @api.depends(
        "picking_id",
        "picking_id.picking_type_id",
        "product_id",
        "product_id.product_tmpl_id",
        "product_id.product_tmpl_id.brand_ids",
        "product_id.product_tmpl_id.brand_ids.code",
    )
    def _compute_product_brand_code(self):
        for operation in self:
            my_brand_code = ""
            my_brand_supplier = ""
            if operation.product_id:
                brands = operation.product_id.product_tmpl_id.mapped(
                    "brand_ids"
                ).filtered(lambda x: x.code)
                for brand in brands:
                    my_brand_code = (
                        brand.code
                        if not my_brand_code
                        else "{}, {}".format(my_brand_code, brand.code)
                    )
                    if brand.partner_id:
                        my_brand_supplier = (
                            brand.partner_id.name
                            if not my_brand_supplier
                            else "{}, {}".format(
                                my_brand_supplier, brand.partner_id.name
                            )
                        )
            if my_brand_code != operation.product_brand_code:
                operation.product_brand_code = my_brand_code
            if my_brand_supplier != operation.brand_supplier:
                operation.brand_supplier = my_brand_supplier

    product_brand_code = fields.Char(
        string="Product brand code", compute="_compute_product_brand_code", store=True
    )
    brand_supplier = fields.Char(
        string="Fabricator", store=True, compute="_compute_product_brand_code"
    )

    @api.model
    def run_scheduler_stock_pack_ope_product_brand_code(self):
        cond = []
        operations = self.env["stock.pack.operation"].search(cond)
        for operation in operations:
            try:
                my_brand_code = ""
                if operation.product_id:
                    brands = operation.product_id.product_tmpl_id.mapped(
                        "brand_ids"
                    ).filtered(lambda x: x.code)
                    for brand in brands:
                        my_brand_code = (
                            brand.code
                            if not my_brand_code
                            else "{}, {}".format(my_brand_code, brand.code)
                        )
                if my_brand_code != operation.product_brand_code:
                    self.env.cr.execute(
                        "update stock_pack_operation set product_brand_code=%s where id=%s",
                        (my_brand_code, operation.id),
                    )
            except Exception:
                pass
