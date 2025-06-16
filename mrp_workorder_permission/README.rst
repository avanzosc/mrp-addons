.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

========================
MRP Workorder Permission
========================

This module extends manufacturing work orders in Odoo to improve user assignment and access control based on responsibilities in the production process.

Main Features
=============

* Adds a **User** field (`user_id`) to manufacturing work orders (`mrp.workorder`), allowing the assignment of a responsible user.
* Adds a **Default User** field (`default_user_id`) to work centers (`mrp.workcenter`), used to automatically assign a user to work orders.
* Automatically assigns the work order's user based on the default user of the selected work center when the work order is created.
* When the work center is changed in an existing work order:
  * If the new work center has a default user, the work order's user is updated accordingly.
  * If the new work center has no default user, the current user remains unchanged.
* User field is visible and editable in the tree, form, and calendar views of work orders.
* Default User field is visible in the tree views of work centers.
* Implements record rules to control work order visibility:
  * **Manufacturing Managers** can view and manage all work orders.
  * **Manufacturing Users** can only view, edit, and create work orders assigned to themselves, and only in the *Confirmed* or *In Progress* state.

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

* Berezi Amubieta <bereziamubieta@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Lucía Echeverría <luciaavanzosc@gmail.com>
* Ana Juaristi <anajuaristi@avanzosc.es>