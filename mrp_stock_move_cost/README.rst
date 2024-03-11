.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===================
Mrp stock move cost
===================

* When closing the MO if the MO has a LOT: In the Unit price field of the LOT,
  enter the sum of the cost of products consumed / number of units produced.
* In the move line of the product produced, the cost is equal to the sum of the
  cost of products consumed, and the unit price is equal to its cost / quantity
  produced.
* When change the purchase price of the lot, changes the cost of the OFS
  associated with that lot.

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
