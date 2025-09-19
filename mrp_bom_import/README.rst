.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
MRP BoM Import
==================

Module to import **Bills of Materials (BoM)** from Excel files, improving usability and automation in manufacturing operations.

* Allows importing BoMs and component lines from structured Excel files.
* Automatically validates parent products, component products, quantities, and references.
* Creates BoMs and BoM lines directly from imported data.
* Provides a log of errors and highlights issues in import lines.
* Quick access to imported lines and created BoMs.

Key Features
============

- Wizard to upload Excel files and import BoMs.
- Validation of imported lines, with error reporting in **Log Info**.
- Automatic creation of **BoMs** and **BoM Lines** from valid lines.
- Search, filter, and group by **Parent Product**, **Component Product**, **Reference**, and **State**.
- Statusbar and state management for import workflow (`draft`, `2validate`, `pass`, `error`, `done`).
- Tree, form, and search views for **BoM Import Lines** with decorations to highlight errors and processed lines.

Configuration
=============

1. Go to **Manufacturing → Configuration → BoM Import**.
2. Upload an Excel file using the column names in the **Help** tab:
   - `Product Code`, `Product Name`, `Quantity`
   - `Parent Code`, `Parent Name`, `Parent Qty`
   - `BoM Ref`
3. Click **Validate** to check imported lines.
4. Click **Process** to create BoMs from valid lines.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us improve it by providing detailed feedback.

Credits
=======

Authors
-------

* AvanzOSC

Contributors
------------

* Daniel Campos <danielcampos@avanzosc.es>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>
