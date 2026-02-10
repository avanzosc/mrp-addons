.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================================
Sale order manufacturing order inspection
=========================================

* New object "Quanlity Control Test Labels".
* In "Quality control test" object new field "Test Labels".
* In the "Product Quality Control" section, a new field, "Product Service,"
  has been added.
* In manufacturing orders, a new field "customization" is added for service type
  products.
* When confirming the sales order, for each line, if there is one in the product
  quality control lines that is "Manufacturing", and that has the same product
  or service as any of the lines in the order, take that service to the MO. If
  there is no service but there is a trigger by MO, the product service to the
  NO will not be available.
* In manufacturing order new action "Create Inspection".
* After confirming a sales order and creating the manufacturing orders, the new
  action "Create Inspection" will be executed, as many times as the test has
  test labels.

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
~~~~~~~~~~~~

* Ana Juaristi <anajuaristi@avanzosc.es>
* Alfredo de la Fuente<alfredodelafuente@avanzosc.es>

