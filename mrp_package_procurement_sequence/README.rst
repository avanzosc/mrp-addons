.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://opensource.org/licenses/AGPL-3.0
   :alt: License: AGPL-3

================================
MRP Package Procurement Sequence
================================

This module enhances MRP by adding automatic package naming and improved visibility of packaged finished products.

Key Features
============

- Extends `stock.move.line` to generate package names like: PREFIX-01, PREFIX-02, ...
- Uses the procurement group's packaged count to ensure consistent numbering.
- Adds a computed field on `procurement.group` that counts finished move lines already assigned to packages.
- `mrp.production` shows the packaged count through a related field.
- Provides an action to list all packaged finished move lines linked to the same procurement group.

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



