.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://opensource.org/licenses/AGPL-3.0
   :alt: License: AGPL-3

========================
MRP BOM Create Movelines
========================

This module automatically brings BOM components to the manufacturing
order's input lines when the order is confirmed, so they can be
consumed without needing a prior lot/serial reservation.

It adds a "Bring Components on Confirm" option on the BOM category.
When a manufacturing order uses a BOM whose category has this option
enabled, confirming the order creates an empty stock move line for
each storable component that doesn't already have one, ready to be
filled in during production.

Key Features
============

* Adds a "Bring Components on Confirm" flag on BOM categories.
* On manufacturing order confirmation, automatically creates input
  move lines for storable components of BOMs belonging to a category
  with that flag enabled.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted
it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Ana Juaristi <anajuaristi@avanzosc.es>
* Lucía Echeverría <luciaecheverria@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.



