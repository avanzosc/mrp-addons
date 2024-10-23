.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================================
MRP BOM Line and BOM Report Enhancements
========================================

Functionality
-------------

- **Enhanced BoM Line Report**: Adds additional columns and formatting to the Bill of Materials (BoM) line report. Includes calculations for product quantity multiplied by product cost, formatted with currency symbols.
- **Enhanced BoM Report**: Extends the BoM report with new columns for calculated costs and quantities, formatted with currency symbols. Adds columns in both the header and footer sections to provide additional details for product costs and totals.

Details of Changes
------------------

### BoM Line Report (`report_mrp_bom_line_inherit`)

- **Column 6**: Adds a new column that shows the calculated value of `prod_qty * prod_cost`, formatted according to the currency's position (before or after the amount).
- **Column 3**: Removes the original content and replaces it with a new column that displays the `prod_qty`, formatted to four decimal places.
- **Column 5**: Removes the original content and replaces it with a new column that shows `prod_cost`, formatted similarly to the new column in column 6.
- **Column 6 (footer)**: Removes the original content and replaces it with a new column that shows the `total` value divided by `bom_qty`, formatted with currency symbols.

### BoM Report (`report_mrp_bom_inherit`)

- **Header Column 6**: Adds a new header column for "Prod Qty * Prod Price" if the report structure is not 'bom_structure'.
- **Footer Column 5**: Adds a new footer column that displays the calculated value of `price / bom_qty`, formatted with currency symbols.
- **Footer Column 6**: Adds a new footer column showing `total / bom_qty`, formatted with currency symbols.
- **Columns 3 and 5 in tbody**: Adds new columns for `bom_qty` and `price`, respectively, formatted with currency symbols.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/avanzosc/odoo-addons/issues>`_. In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Ana Juaristi <anajuaristi@avanzosc.es>
* Unai Beristain <unaiberistain@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.
