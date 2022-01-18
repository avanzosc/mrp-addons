# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Manufacturing Product Density",
    "version": "12.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "mrp",
        "product_density",
    ],
    "data": [
        "views/mrp_production_view.xml",
        "views/mrp_workorder_view.xml",
    ],
    "installable": True,
}
