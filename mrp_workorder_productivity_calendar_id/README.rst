.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0.html
   :alt: License: LGPL-3

====================================
MRP Workcenter Productivity Calendar
====================================

Overview
========

The **MRP Workcenter Productivity Calendar** module adds the ability to assign a work schedule (resource calendar) to work center productivity records in the **Manufacturing** module. It automatically sets the work schedule based on the employee assigned to the user when creating or updating a record. This work schedule is visible and editable in the **Workcenter Productivity** form and tree views.

Features
========

- Adds a **`calendar_id`** field (Work Schedule) to the **`mrp.workcenter.productivity`** model.
- The **`calendar_id`** field is automatically populated based on the employee's work schedule when a user is assigned to a work center productivity record.
- Displays the **`calendar_id`** field in both the form and tree views for **Workcenter Productivity**.
- The work schedule is fetched from the associated employee when the **user_id** is selected or changed.

Usage
=====

1. Go to **Manufacturing** > **Work Centers** > **Workcenter Productivity**.
2. When a user is selected for a productivity record, the work schedule (calendar) is automatically populated based on the assigned employee's work schedule.
3. The **`calendar_id`** field can be edited directly in the form or tree views, where it will be displayed next to the **user_id** field.

Configuration
=============

No additional configuration is required. The module relies on the **employee's resource calendar** to set the work schedule.

Testing
=======

1. Create a new **Workcenter Productivity** record.
2. Select a user and verify that the **`calendar_id`** field is automatically populated with the corresponding work schedule.
3. Edit the **`calendar_id`** field and confirm that the change is saved.

Bug Tracker
===========

Bugs and issues can be reported on the GitHub repository:
`GitHub Issues <https://github.com/avanzosc/odoo-addons/issues>`_.

Credits
=======

Contributors
------------

* Ana Juaristi <anajuaristi@avanzosc.es>
* Aner Arregi <aneravanzosc@gmail.com>

For further information, please contact the contributors.

License
=======

This project is licensed under the LGPL-3 License.
For more details, see the LICENSE file or visit:
<https://www.gnu.org/licenses/lgpl-3.0.html>.
