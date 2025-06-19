.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=====================================
MRP Stock Action Show Details Context
=====================================

This module customizes the behavior of the **"Show Details"** button (`action_show_details`) on stock moves related to manufacturing orders in Odoo.

When a stock move is linked to a manufacturing order (`raw_material_production_id` or `production_id`), the module modifies the context of the resulting action to dynamically control how lot/serial number fields are displayed based on the configuration of the operation type (`picking_type_id`):

* If the picking type has **"Auto Consume Component Lots"** enabled (`use_auto_consume_components_lots`), the action will display a **Many2one** field for selecting existing lots.
* If the picking type has **"Create Component Lots"** enabled (`use_create_components_lots`), the action will display a **text field** for entering new lot names.
* If neither option is enabled, both fields will be hidden.

This allows for more flexible and context-sensitive handling of lot/serial numbers during manufacturing operations.

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

* Lucía Echeverría <luciaavanzosc@gmail.com>
* Ana Juaristi <anajuaristi@avanzosc.es>