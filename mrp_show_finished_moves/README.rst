.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://opensource.org/licenses/AGPL-3.0
   :alt: License: AGPL-3

=======================
MRP Show Finished Moves
=======================

This module extends the Manufacturing (MRP) functionality to improve the visibility and editability of finished stock moves and move lines within Manufacturing Orders (MOs) and Work Orders (WOs).

**Features**

- **New Finished Moves Tab**
  - Adds a **"Finished Moves"** tab in both the MO and WO forms to display finished stock moves and move lines.

- **Stat Button on Manufacturing Orders**
  - Adds a stat button to MOs that opens a dedicated tree view with all related finished move lines.

- **Finished Move Lines Menu**
  - Provides a new menu entry under *Manufacturing* to access all finished move lines directly.

- **Automatic Lot Assignment**
  - When creating finished move lines, the system automatically assigns the **production lot** (if available and required by the product’s tracking).

- **Editable Stock Moves Tree**
  - Makes stock moves editable from the tree view.
  - Hides less relevant fields (e.g., `date`, `company_id`, `reference`).
  - Adds useful optional fields (`lot_ids`, `workorder_id`).
  - Introduces a **"Show Details"** button that opens move details in the current window.

- **Quantity Consistency Checks**
  - On marking an MO as done:
    - Compares MOs **Quantity Producing** vs **MO Finished Moves Quantity Done**.
    - Compares **Work Order Produced Quantity** vs **MO Finished Moves Quantity Done**.
  - If mismatches are detected, a **warning wizard** is shown with the option to:
    1. Adjust `qty_producing` and `qty_produced` in both MO and WOs to match `quantity_done`.
    2. Or stop and review data before proceeding.

- **Wizard for Discrepancies**
  - A dedicated transient model **`mrp.production.qty.warning`** warns about inconsistencies.
  - Provides **customizable Yes/No actions**:
    - **Yes**: corrects discrepancies and proceeds with marking MO as done.
    - **No**: cancels and allows user to review data.

- **Synchronization of Quantities**
  - Updates `qty_producing` and `qty_produced` across MO and WOs whenever the user accepts corrections.

- **Enhanced Finished Move Form**
  - Replaces reserved availability with **product quantity** for better tracking.
  - Improves integration with immediate transfers.

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
* Lucía Echeverría <luciaecheverria@avanzosc.es>

For specific questions regarding this module, please contact the contributors. For support, please use the official issue tracker.

License
=======

This project is licensed under the AGPL-3 License. For more details, refer to the LICENSE file or visit <https://opensource.org/licenses/AGPL-3.0>.
