.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://opensource.org/licenses/LGPL-3.0
   :alt: License: LGPL-3

=====================================================
MRP BoM Import with Layer and Designator Enhancements
=====================================================

Overview
========

The **MRP BoM Import with Layer and Designator** module extends the functionality of the Bill of Materials (BoM) import process in Odoo. It adds support for additional fields like *Layer* and *Designator* when importing BoM lines, making the import process more flexible and aligned with manufacturing requirements involving complex electronic components and layered structures.

Features
========

- **BoM Import Enhancements**:
  
  - Adds two new fields, *Layer* and *Designator*, to the BoM import process.
  
  - The *Layer* field allows users to specify the production layer for each imported component.
  
  - The *Designator* field is used to assign component designators during the import process.

Usage
=====

Once the module is installed:

- Go to the **Manufacturing** module in Odoo.
  
- When importing a Bill of Materials (BoM), two new fields, *Layer* and *Designator*, will be available in the import lines interface.

- These fields allow you to better categorize and organize your BoM components based on specific production or assembly needs.

Configuration
=============

1. **Install the Module**:

   - Ensure that the dependent modules `mrp_bom_import` and `mrp_bom_line_layer_and_designator` are installed and configured correctly.

2. **BoM Import Process**:

   - Customize the BoM import template to include the new fields *Layer* and *Designator* if needed.

Testing
=======

Test the following scenarios:

- **BoM Import**:
  
  - Import a BoM with various components and ensure the *Layer* and *Designator* fields are correctly processed.
  
  - Verify that the imported components are displayed with their respective *Layer* and *Designator* in the BoM lines.

Bug Tracker
===========

For bugs and issues, please visit `GitHub Issues <https://github.com/avanzosc/project-addons/issues>`_ to report or track issues.

Credits
=======

Contributors
------------

* Unai Beristain <unaiberistain@avanzosc.es>

* Ana Juaristi <anajuaristi@avanzosc.es>

Please contact contributors for module-specific questions, but direct support requests should be made through the official channels.

License
=======
This project is licensed under the LGPL-3 License. For more details, please refer to the LICENSE file or visit <https://opensource.org/licenses/LGPL-3.0>.
