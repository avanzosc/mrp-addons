.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

================
MRP Product Loss
================

This module extends the **Manufacturing (MRP)** and **Inventory** applications to manage and track product loss quantities during the production process.  

Key Features
============

- **Product Loss Quantity**  
  Each product template can be configured with a default *loss quantity* to be consumed during manufacturing.

- **BOM Line Integration**  
  The Bill of Materials (BoM) lines display and inherit the product’s configured loss quantity.

- **Stock Moves Extension**  
  - New fields:
    - `to_consume_before_loss_qty`: Quantity to consume before loss adjustment.
    - `product_loss_qty`: Computed loss quantity per move.
  - Automatic calculation of loss quantity during move creation and production updates.

- **Production Order (MRP)**  
  - Automatically computes and assigns loss quantities to raw material moves.  
  - Adjusts `to_consume_before_loss_qty` and `product_loss_qty` dynamically when producing quantities change.  
  - Extends `_get_move_raw_values` to include additional consumption with loss.

- **User Interface Enhancements**
  - **BoM Form**: Adds `Loss Quantity` in BoM lines.  
  - **Manufacturing Orders**: Displays `To Consume Before Loss Quantity` and `Loss Quantity` in raw material moves.  
  - **Products**: Adds `Loss in products to be consumed` in the product form and list views.  
  - **Stock Moves**: Displays additional fields (`to_consume_before_loss_qty`, `product_loss_qty`).

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
------------

* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>
