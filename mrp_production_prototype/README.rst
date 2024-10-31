.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

========================
Mrp production prototype
========================

* In manufacturing orders 2 new fields: "Is Prototype?", "Prototype Validation
  Date".
* If the manufacturing order is not a prototype, you can select a manufacturing
  order that is a prototype, and that has the same parent product.
* Hide "plan" and "done" buttons for orders that have a prototype assigned
  whose status is different from DONE and have an empty validation date.

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
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
