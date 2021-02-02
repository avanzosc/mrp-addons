# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, tools


class StockInventoryProductVersionReport(models.Model):
    _name = "stock.inventory.product.version.report"
    _description = "Inventory Report with Product Version"
    _auto = False

    name = fields.Many2one(comodel_name='stock.move',
                           string='Name')
    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Version")
    location_id = fields.Many2one(comodel_name="stock.location",
                                  name="Location")
    product_qty = fields.Float(string="Qty")
    real_product_qty = fields.Float(string="Real Qty")
    virtual_product_qty = fields.Float(string="Virtual Qty")
    sale_id = fields.Many2one(comodel_name='sale.order.line',
                              string='Sale')
    purchase_id = fields.Many2one(comodel_name='purchase.order.line',
                                  string='Purchase')
    mrp_id = fields.Many2one(comodel_name='mrp.production',
                             string='Production')
    product_id = fields.Many2one(comodel_name='product.product')

    @api.model_cr
    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr,
                                  'stock_inventory_product_version_report')
        self._cr.execute("""
            CREATE VIEW stock_inventory_product_version_report
                AS (
                    SELECT
                        min(ml.id) as id,
                        ml.product_version_id as product_version_id,
                        ml.product_id as product_id,
                        ml.location_id,
                        sum(ml.real_stock + ml.virtual_stock) as product_qty,
                        sum(ml.real_stock) as real_product_qty,
                        sum(ml.virtual_stock) as virtual_product_qty
                    FROM
                        stock_move as ml
                    GROUP BY
                        ml.product_id, ml.product_version_id, ml.location_id)
        """)
