.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://opensource.org/licenses/AGPL-3.0
   :alt: License: AGPL-3

=======================
MRP Show Finished Moves
=======================

This module improves the visibility of finished moves within Manufacturing
Orders (MOs) and Work Orders (WOs). It adds smart buttons, dedicated tabs,
and enhanced serial/lot tracking to give operators full traceability over
what has been produced.

Features
========

Manufacturing Orders
--------------------

* **Finished Moves smart button** — opens the list of finished move lines
  linked to the MO and all its related backorders (grouped by procurement
  group).
* **Result Packages smart button** — opens the list of destination packages
  produced by the MO.
* **Finished Moves tab** — a dedicated page inside the MO form showing
  ``move_finished_ids`` inline.
* **Produced / Producing columns** in the MO list view for at-a-glance
  progress tracking.
* **Last Manufactured Lot** computed field (visible for serial-tracked
  products) that shows the most recently produced serial number for the
  product, used as the seed for auto-generation.
* **Quantity Discrepancy Warning wizard** — when marking an MO as done,
  if the *Quantity Producing* reported by the MO or any Work Order does not
  match the actual quantity recorded in the finished moves, a dialog is
  shown. The user can choose to automatically align all quantities before
  closing, or go back to review the data.

Work Orders
-----------

* **Finished Move Lines smart button** — opens finished move lines scoped
  to the WO's production group.
* **Result Packages smart button** — opens destination packages for the WO.

Serial / Lot Auto-Generation
-----------------------------

* On **confirmation** of a serial-tracked MO, serial numbers are
  auto-generated for the finished move lines starting from the next
  incremented serial after the last manufactured lot.
* Whenever **qty_producing** or **lot_producing_id** changes on an MO
  (serial or lot tracking), the finished move lines are automatically
  regenerated:

  * *Serial products*: one move line per unit, serials incremented
    sequentially.
  * *Lot products*: a single move line with the current lot and the new
    quantity.

* When the quantity on a finished stock move is edited directly (e.g. from
  the Finished Moves tab), ``qty_producing`` on the MO is kept in sync
  automatically, and serial/lot lines are regenerated accordingly.
* On **split** (backorder creation), each new MO gets its own serials
  auto-generated from the last manufactured lot.
* After **marking an MO as done**, backorder MOs refresh their
  ``last_manufactured_lot`` and regenerate their serial lines accordingly.

Stock Move Improvements
------------------------

* **action_show_details** opens inline (``target: current``) instead of in
  a dialog, and pre-populates the *Generate Serials* dialog with the next
  serial number and the planned quantity via context keys
  ``mo_next_serial`` and ``mo_product_qty``.
* ``display_assign_serial`` is forced to ``True`` for finished moves of
  serial-tracked products so the assign-serial widget is always available.
* Raw consumption moves are **auto-picked** when their quantity reaches the
  expected consumption amount, avoiding manual confirmation steps.
* Reservation (``action_assign``) is scoped to the qty_producing / product_qty
  ratio so only the stock needed for the current production run is reserved.

JavaScript Enhancement
-----------------------

* The ``generate_serials`` view widget is patched so that when opening the
  serial generation dialog from an MO context, the *Next Serial* and
  *Count* fields are pre-filled with ``mo_next_serial`` and
  ``mo_product_qty`` and *Keep existing lines* is unchecked.

Usage
=====

#. Open any Manufacturing Order in the **Manufacturing** app.
#. Use the **Finished Moves** or **Result Packages** smart buttons in the
   top-right button box to inspect produced items and packages.
#. Switch to the **Finished Moves** tab in the MO form to view or edit
   finished stock moves directly.
#. When producing serial-tracked items, serial numbers are generated
   automatically. You can also trigger generation manually via the
   **Generate Serials** button on the finished move detail view.
#. When clicking **Mark as Done**, if a quantity mismatch is detected a
   warning dialog will appear. Choose **Yes, adjust quantities and proceed**
   to let the system align all quantities automatically, or **No, review
   data first** to go back and correct manually.
#. On Work Orders, use the same **Finished Move Lines** and **Result
   Packages** smart buttons to inspect production output at the operation
   level.

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
