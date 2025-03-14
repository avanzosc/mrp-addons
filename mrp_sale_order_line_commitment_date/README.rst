.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0.html
   :alt: License: LGPL-3

===================================
MRP Sale Order Line Commitment Date
===================================

Overview
========

The **MRP Sale Order Line Commitment Date** module allows the display and management of the **Commitment Date** from the related sale order line in the `mrp.production` model. This is useful for tracking the commitment date of the sale order line associated with a manufacturing order and ensures that the commitment date is updated in child manufacturing orders.

Features
========

- Adds a **Commitment Date** field to the `mrp.production` model.
- The **Commitment Date** field is displayed on the **Production Order** form view and is related to the corresponding **Sale Order Line**.
- The **Commitment Date** field is read-only and is automatically updated when the related Sale Order Line is updated.
- The **Commitment Date** field is also shown in the tree view of Manufacturing Orders.
- Updates the **Commitment Date** field for all related child manufacturing orders when the parent manufacturing order is updated.

Usage
=====

1. Go to **Manufacturing → Manufacturing Orders**.
2. Open any manufacturing order.
3. In the **General Information** tab, you will see the **Commitment Date** field populated from the related Sale Order Line.
4. The **Commitment Date** field will also be visible in the tree view of Manufacturing Orders.
5. If the **Commitment Date** is updated in the parent manufacturing order, it will automatically update the corresponding child manufacturing orders as well.

Configuration
=============

No additional configuration is required.

Testing
=======

1. Create a **Sale Order** with a **Sale Order Line** containing a commitment date.
2. Create a **Manufacturing Order** linked to that **Sale Order Line**.
3. Verify that the **Commitment Date** is automatically displayed in the Manufacturing Order form view and tree view.
4. Update the **Commitment Date** in the parent Manufacturing Order and check that the child manufacturing orders are also updated with the same date.

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
