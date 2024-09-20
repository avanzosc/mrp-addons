.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
MRP BOM Structure XLSX Cost
===========================

This module provides an XLSX report detailing the BOM (Bill of Materials) structure at the product level. It utilizes Odoo’s XLSX reporting engine and XlsxWriter library.

Overview
--------

### Class `BomStructureXlsxL1`

- **Purpose**: Generates a Level 1 BOM structure report in XLSX format.
- **Inherits**: Extends `report.mrp_bom_structure_xlsx.bom_structure_xlsx`.

### Key Methods

- **`print_bom_children(self, ch, sheet, row, level)`**:
  - Writes BOM line details to the XLSX sheet, including product code, name, quantity, unit of measure, reference, and cost.
  - Recursively processes child BOM lines.

- **`generate_xlsx_report(self, workbook, data, objects)`**:
  - Configures the XLSX workbook and sheet, sets column widths, applies formatting, and writes report data.
  - Calls `print_bom_children` to include child BOM lines.

### Report Configuration

- **Sheet Layout**: Landscape orientation, 80% zoom, with adjusted column widths.
- **Formatting**: Bold headers and data rows.
- **Freezing Panes**: Keeps the header row visible when scrolling.

This setup allows for a detailed and organized BOM report in an easy-to-read XLSX format.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Ana Juaristi <ajuaristio@gmail.com>
* Unai Beristain <unaiberistain@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.
