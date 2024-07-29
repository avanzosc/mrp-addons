.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
MRP BOM Structure XLSX Cost
===========================

Functionality
-------------

- **Export BoM Structure**: Allows users to export the BoM structure of products to Excel format.
- **Level 1 Report**: Specifically exports Level 1 details including product codes, names, quantities, unit of measure, BoM codes, and calculated costs based on standard prices.
- **Excel Format**: Outputs data in .xlsx format suitable for further analysis or reporting purposes.

Model Details
-------------

- `BomStructureXlsxL1` (Abstract Model):
  - Defines the structure and content for exporting Level 1 BoM reports to Excel.
  - Computes and writes product details including default code, display name, quantity, unit of measure, BoM code, and calculated cost.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/odoo-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Ana Juaristi <anajuaristi@avanzosc.es>
* Unai Beristain <unaiberistain@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.
