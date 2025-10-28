.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

====================
Mrp qty by packaging
====================

This module extends the standard **MRP (Manufacturing) functionality** by integrating **product packaging management** into manufacturing orders. It allows users to define packaging types and quantities for products, automatically calculating the required production quantities based on packaging.

Key Features
============

- **Add Packaging to Manufacturing Orders**
  - Select a `product_packaging_id` for a manufacturing order.
  - Display and edit the corresponding `product_packaging_qty`.

- **Automatic Quantity Calculation**
  - When a packaging is selected, the module automatically calculates the production quantity based on the packaging quantity.
  - Updating the packaging quantity updates the production quantity, and vice versa.

- **Integration with Stock Rules**
  - Manufacturing orders created via stock rules inherit the packaging information from the associated sale order line.

- **User Interface Enhancements**
  - Extended **Manufacturing Order form view** to include packaging fields.
  - Added packaging columns to the **tree view** and **filters** in manufacturing orders.

- **Consistency on Quantity Changes**
  - When production quantity is modified while the order is confirmed, the system updates packaging quantities accordingly using the change quantity wizard.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted
it first, help us smash it by providing detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Contributors
~~~~~~~~~~~~

* Ana Juaristi <anajuaristi@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
