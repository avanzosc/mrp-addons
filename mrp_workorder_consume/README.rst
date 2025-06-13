======================
MRP Work Order Consume
======================

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1|

This module enables the ability to post inventory directly from a Work Order in Manufacturing Orders in Odoo. 
It provides an additional control mechanism to mark the production as done when specific conditions are met, improving usability for technical users and streamlining inventory operations.

Key Features
=============

- Adds a **"Post Inventory"** button to the Work Order form and tree views.
- The button becomes visible **only when**:
  - The Work Order is in **'Done'** state.
  - There are raw material moves with some **quantity marked as done**.
- Posting inventory will trigger the **`Mark as Done`** action on the corresponding Manufacturing Order.
- Adds a **"Finished Moves"** tab in both the Work Order and Manufacturing Order views.
- Enhances the stock move tree view with extra fields and usability improvements, including:
  - Editable lines from the bottom.
  - Display of related Work Order.
  - Button to open detailed lines for finished products.

Technical Details
=================

- Introduces a computed field `post_visible` in `mrp.workorder` to determine the visibility of the "Post Inventory" button.
- Adds XML view customizations to:
  - Extend the `mrp.production` and `mrp.workorder` form views with the "Finished Moves" tab.
  - Add the "Post Inventory" button to the header and tree views of Work Orders.
  - Customize the `stock.move` tree view (`view_move_tree`) to support:
    - Better editing experience.
    - Display and management of fields like `workorder_id`, `quantity_done`, `lot_ids`, etc.
    - Inline actions like "Show Details" for finished moves.

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* AvanzOSC

Contributors
~~~~~~~~~~~~

* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Lucía Echeverría <luciaavanzosc@gmail.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
