.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0.html
   :alt: License: LGPL-3

==========================
MRP Production Origin Sale
==========================

Overview
========

The **MRP Production Origin Sale** module modifies the **origin** field in the **Manufacturing Orders** (MO) to include the reference to the original **Sales Order** (SO). This enhancement helps trace the original Sales Order in child manufacturing orders when they are created from a parent manufacturing order.

Features
========

- Enhances the **origin** field in both parent and child manufacturing orders.
- When a child manufacturing order is created, its **origin** field will now contain both the parent MO and the Sales Order reference, making it easier to trace the original Sales Order.
- The **origin** field will follow this structure for child orders: `Parent MO - SO123`.

Example
========

Before the change:
-------------------

- **Sales Order (SO001)**
  
  - **Parent Manufacturing Order (MO001)** (`origin: SO001`)
  
  - **Child Manufacturing Order (MO002)** (`origin: MO001`)

After the change:
-----------------

- **Sales Order (SO001)**
  
  - **Parent Manufacturing Order (MO001)** (`origin: SO001`)
  
  - **Child Manufacturing Order (MO002)** (`origin: MO001 - SO001`)

This change makes it easier to track the origin of manufacturing orders and their relationships with the Sales Orders.

Usage
=====

1. Create a **Sales Order** and confirm it.
2. Generate a **Manufacturing Order (MO)** from the Sales Order.
3. If there are child manufacturing orders, you will now see the reference to both the parent MO and the Sales Order in their **origin** field.

Configuration
=============

No additional configuration is required. The module works out of the box when creating manufacturing orders from a Sales Order.

Testing
=======

1. Create a **Sales Order** and confirm it.
2. Generate a **Parent Manufacturing Order (MO)**.
3. Verify that the **origin** field in the parent MO references the Sales Order.
4. Create a **Child Manufacturing Order (MO)** from the parent MO and check that its **origin** field includes both the parent MO and the Sales Order reference.

Bug Tracker
===========

Bugs and issues can be reported on the GitHub repository:
`GitHub Issues <https://github.com/avanzosc/odoo-addons/issues>`_.

Credits
=======

Contributors
------------

* Ana Juaristi <anajuaristi@avanzosc.es>
* Unai Beristain <unaiberistain@avanzosc.es>

For further information, please contact the contributors.

License
=======

This project is licensed under the LGPL-3 License.
For more details, see the LICENSE file or visit:
<https://www.gnu.org/licenses/lgpl-3.0.html>.
