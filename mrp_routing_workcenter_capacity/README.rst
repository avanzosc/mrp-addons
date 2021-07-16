.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===============================
MRP Routing workcenter capacity
===============================

* In MRP operations new fields capacity, time before production, and time after
  production.
* When calculating the "Expected Duration" of the OF work orders, it will take
  the capacity defined in the operation, not the one defined in the Work
  Center.
* The fields "Time before prod.", "Time after prod." defined in the operation
  also participate in the calculation, if they are informed. If they are not
  informed, those of the Work Center will be used. 

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
