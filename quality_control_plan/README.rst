.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Quality Control Plan
====================

Module to manage samples to test externally.
* A product can be subjected to a control plan or not.
- If a product is subjected to a control plan, we must define a sample qty
  and scheduled external tests.

* When a product subjected to a control plan is purchased to a supplier, the
  system will check if a Sample Purchase Order must be created for that
  product.
* Sample Order will be created for each product-test relation which its next
  date is lower than the purchase approve date.
* Every time a sample order is created, the related product-test line's next
  date field will be updated based in the interval parameters defined in the
  line.
* New categorization field in tests, to categorize internal and external
  tests.
- If a test is defined as external, is necesary to define at least one
  external laboratory.
- External laboratory is a partner which has checked the external
  laboratory field.

* When a sample for a product is requested, the quantity requested will be
  produts sample qty multiplied by the number of external laboratories
  defined in the test.
* When a sample order is approved, the purchase line will be divided in
  several picking lines, one for each external laboratory in the test. And
  linked to each incoming picking line, one outgoing picking will be created.
* When the incoming picking for sample products is transferred, the lot
  transferred to the sample product will be set as restrict lot to origin
  purchase's move line. And it will be locked until the external test is
  resolved.


Credits
=======

Contributors
------------
* Ainara Galdona <ainaragaldona@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>
