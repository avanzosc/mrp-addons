# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Packaging Is Pallet",
    "summary": "Glue module to show packagings by pallet status.",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp_qty_by_packaging",
        "product_packaging_is_pallet",
    ],
    "data": ["views/mrp_production_view.xml"],
    "installable": True,
    "auto_install": True,
}
