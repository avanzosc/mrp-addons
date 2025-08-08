.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://opensource.org/licenses/AGPL-3.0
   :alt: License: AGPL-3

=================================
MRP Workorder Quant Manual Assign
=================================

This module adds a **Manual Quants** button to the **Work Order** form view in the Manufacturing module. The button allows users to manually assign stock quants during production.

**Key Features**

* Adds a "Manual Quants" button in the `move_raw_ids` list of work orders.
* The button triggers the `stock_quant_manual_assign` action.
* Visibility of the button is restricted to specific work order states: `confirmed`, `assigned`, and `partially_available`.

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

* Ana Juaristi <anajuaristi@avanzosc.es>
* Lucía Echeverría <luciaecheverria@avanzosc.es>

For specific questions regarding this module, please contact the contributors. For support, please use the official issue tracker.

License
=======

This project is licensed under the AGPL-3 License. For more details, refer to the LICENSE file or visit <https://opensource.org/licenses/AGPL-3.0>.
