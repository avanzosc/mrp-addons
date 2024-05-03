# -*- coding: utf-8 -*-
# © Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Product multi brand",
    "version": "8.0.2.0.0",
    "license": "AGPL-3",
    "depends": [
        "product_code_builder",
        "product_supplierinfo_for_customer",
        "jvv_custom",
        "product_by_supplier",
        "jvv_product_supplierinfo_certifications"
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "category": "",
    "summary": "",
    "data": [
        "data/product_brand_multi_data.xml",
        "views/product_view.xml",
        "views/product_brand_view.xml",
        "security/ir.model.access.csv",
        "views/purchase_order_views.xml",
        "views/purchase_order_line_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "report/purchase_order_report.xml",
        "report/stock_picking_report.xml",
    ],
    "installable": True,
}
