.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
MRP Manufacturing Order Stock Picking Link
==========================================


Overview
========

The **MRP Manufacturing Order Stock Picking Link** module provides an integration between manufacturing orders and internal stock pickings in Odoo. This module enhances the relationship between these two entities by adding direct links, shortcuts, and filters to streamline the workflow.

Features
========

- **Link Manufacturing Orders and Pickings**:
  - Adds a one-to-many relationship between manufacturing orders and internal stock pickings.

- **Internal Pickings Shortcut**:
  - Adds a button in the manufacturing order form to quickly access the associated internal pickings.

- **Additional Fields in Stock Pickings**:
  - Includes a field in stock pickings to reference the related manufacturing order.

- **Enhanced Views**:

  - **Manufacturing Order View**:
    - Adds a new tab to the manufacturing order form view to list related internal pickings.
    - Provides a button to open the related internal pickings directly.
  - **Stock Picking Views**:
    - Adds a field in the stock picking form and tree views to display the related manufacturing order.

Usage
=====

After installing the module, you will see:

- **Manufacturing Orders**:
  - A new tab named "Internal Pickings" in the manufacturing order form view.
  - A button labeled "Internal Pickings" to quickly open related stock pickings.

- **Stock Pickings**:
  - The stock picking form view will include a field to display the associated manufacturing order.
  - The stock picking tree view will also show the related manufacturing order.

Configuration
=============

No additional configuration is required. The module will automatically enhance the views and add fields as described.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/avanzosc/odoo-addons/issues>`_. If you encounter any issues, please check there to see if your issue has already been reported. If not, provide detailed feedback to help us address it.

Credits
=======

Contributors
------------
* Unai Beristain <unaiberistain@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.

License
=======
This project is licensed under the AGPL-3 License. For more details, please refer to the LICENSE file or visit <http://www.gnu.org/licenses/agpl-3.0-standalone.html>.
