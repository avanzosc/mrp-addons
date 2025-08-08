.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://opensource.org/licenses/AGPL-3.0
   :alt: License: AGPL-3

======================
MRP Production Control
======================

This module extends the Odoo Manufacturing (MRP) application by adding detailed production control capabilities directly linked to Manufacturing Orders and Work Orders.
It allows operators and quality control personnel to record key production data such as pallet numbers, controlled and defective piece counts, defect descriptions, and corrective actions taken during the manufacturing process.

* Production Control Model: A new model mrp.production.control captures detailed control lines with fields like operator, pallet number, controlled pieces, defective pieces, defect description, and actions taken.

* Integration with Manufacturing Orders and Work Orders: Each production control line is linked to a specific Manufacturing Order (mrp.production) and optionally to a Work Order (mrp.workorder). Changes in one automatically update the other to maintain consistency.

* Extended Manufacturing Order and Work Order Models: Adds one-to-many relationships to production control lines, enabling direct access and management of control data from Manufacturing Order and Work Order forms.

* Computed Controlled Pieces Summary: For each Manufacturing Order, the minimum number of controlled pieces across related Work Orders is computed and stored, providing a quick quality control metric.

* User-Friendly Views: Includes a form view for managing production control records with convenient filters and groupings. Also integrates a dedicated "Production Control" page inside the Manufacturing Order and Work Order forms.

* Menu Access: Adds a menu entry under Manufacturing for quick access to all Production Control records.

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

* Lucía Echeverría <luciaavanzosc@gmail.com>

For specific questions regarding this module, please contact the contributors. For support, please use the official issue tracker.

License
=======

This project is licensed under the AGPL-3 License. For more details, refer to the LICENSE file or visit <https://opensource.org/licenses/AGPL-3.0>.
