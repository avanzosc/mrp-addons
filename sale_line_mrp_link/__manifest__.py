# © 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sale MRP Link",
    "version": "12.0.1.0.0",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "sale",
        "sale_stock",
        "mrp",
        "mrp_scheduled_products",
    ],
    "data": [
        "views/sale_view.xml",
        "views/mrp_production_view.xml",
    ],
    "installable": True,
}
