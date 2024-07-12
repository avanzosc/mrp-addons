.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===========================
MRP BOM Sale Price Subtotal
===========================

Overview
--------

Adds sale price and subtotal fields to Bill of Materials (BoM) in Odoo 16.

Features
--------

- Adds a "Sale Price" field related to the product's sale price.
- Calculates and displays a "Subtotal" field as quantity multiplied by the sale price.
- Shows the total of all subtotals in the BoM.

Installation
------------

1. Place the module folder `mrp_bom_sale_price_subtotal` in your Odoo addons directory.
2. Update the Odoo module list by going to Apps -> Update Apps List.
3. Find the module `mrp_bom_sale_price_subtotal` and click on `Install`.

Usage
-----

Once installed, the `mrp_bom_sale_price_subtotal` module will add the "Sale Price" and "Subtotal" fields to the Bill of Materials (BoM) form and tree views. It enhances visibility and calculation capabilities for managing BoMs in manufacturing processes.

Technical Details
-----------------

- The module extends the `mrp.bom` model to include new fields for sale price and subtotal.
- Views are modified using XML templates (`mrp_bom_views.xml`) to integrate the new fields seamlessly into the Odoo user interface.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/odoo-addons/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted
it first, help us smash it by providing detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Contributors
------------

* Unai Beristain <unaiberistain@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>
