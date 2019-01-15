.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==================
MRP production lot
==================

* When a production order is confirmed, a lot is automatically created for the
  product to be manufactured, and this lot will be displayed in the tab
  "Finished products", of the production order form. When creating the lot the
  "Manufacturing date" field will take the value of "Scheduled Date " of the
  OF.

* The expiration dates of the lot will be calculated with the "Manufacturing
  date" field of the batch + the fields of the product.

* When pressing the "fabricate" button in the OF form, in the wizard will be
  shown the created lot, and it can not be modified.

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
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.