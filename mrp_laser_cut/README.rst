.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://opensource.org/licenses/AGPL-3.0
   :alt: License: AGPL-3

=============
MRP Laser Cut
=============

Laser cutting consumes one unit of raw material (a sheet, a plate, a bar,
a coil section...) and cuts several different finished products out of it
in a single run. This module models that operation on top of Odoo
manufacturing.

A **laser cutting order** describes:

* the raw material and how many units of it are processed,
* a **distribution**: one line per finished product, with how much raw
  material each product consumes and how many come out of one raw
  material unit,

and generates a regular manufacturing order that consumes the raw
material and produces every finished product as a byproduct.

Features
========

* **Laser cutting order** (``mrp.laser.cut.order``): raw material,
  quantity of raw material units, and the distribution of finished
  products cut from it.
* **Distribution line** (``mrp.laser.cut.order.line``), one per product:

  * *Consumption*: weight of raw material one unit of the product
    consumes, taken from the raw material line of the product's Bill of
    Materials, or the weight of the product when that Bill of Materials
    does not give it (editable, to account for the cutting loss).
  * *Output*: how many units of the product are cut from one raw material
    unit, entered by hand from the nesting layout or proposed from
    replenishment.
  * *Line consumption* = Consumption x Output.
  * *Total* = order Quantity x Output: the quantity of the product
    produced.

* **Manufacturing order generation**: one button creates the
  manufacturing order from a configurable generic Bill of Materials,
  registers the raw material consumption and one byproduct move per
  distribution line, sets the expected work order duration, and links
  order and production together.
* **Planned figures**: before confirming, the order shows the raw
  material it plans to consume, the part of it the products carry away,
  and the estimated waste (the difference). The estimated waste can never
  be negative: saving a distribution that claims more raw material than
  one unit provides is blocked.
* **Actual figures**: the order tracks - live, across the initial
  manufacturing order and any backorder - the raw material really
  consumed, the part attributable to the products actually produced
  (weighted by the Bill of Materials consumption, so it matches the
  planned figure), the real waste, and the real cutting time. These
  figures are read from the stock moves of the manufacturing order chain,
  plus any stock move linked straight to the order, so an order recorded
  without a manufacturing order (an imported historical order, for
  instance) still reports what it consumed and produced. A **Stock Moves**
  button opens those moves.
* **Offcut material**: an order can be flagged to consume a generic
  offcut (remnant) product instead of a full unit of raw material.
* **Replenishment integration**: a dedicated replenishment screen for the
  laser-cut products; selecting the ones to restock creates draft laser
  cutting orders, grouped by raw material, with the fewest raw material
  units that cover the demand and the least waste, ready for the
  operator to adjust to the real layout.

Configuration
=============

#. In *Manufacturing > Configuration > Settings > Laser Cutting*, set:

   * **Bill of Materials**: the generic Bill of Materials used to create
     the manufacturing orders. Its product is the item those orders
     manufacture (the number of raw material units processed).
   * **Offcut Product**: the generic product proposed as consumed
     material on orders flagged to use offcut material.

#. On the work center used for laser cutting, tick **Laser Work Center**.

#. On each Bill of Materials that cuts a product from a raw material, add
   the raw material as a component whose operation runs on that work
   center. Its **Raw Material** is then detected automatically. The
   quantity of that component line, divided by the quantity the Bill of
   Materials produces, is the raw material one unit of the product
   consumes. It can be given as a weight (kg, g, ...) or in units of raw
   material (0.25 sheets, for instance); in both cases, set the **Weight**
   of the raw material product: it is the weight of one unit of raw
   material.

#. On each finished product, tick **Laser Cut Product** so it shows up in
   the replenishment screen and can be added to a laser cutting order.

Usage
=====

Create an order manually
------------------------

#. Open *Manufacturing > Laser Cutting > Laser Cutting Orders* and create
   a record.
#. Set the **Raw Material**, the **Bill of Materials** and the
   **Quantity** (number of raw material units to process). The **Unit
   Weight** defaults to the weight of the raw material product and follows
   it until a manufacturing order exists; it can be overridden.
#. Add one **Distribution** line per finished product: pick the product
   (its **Consumption** is seeded from the Bill of Materials) and enter
   the **Output** (units per raw material unit) from the cutting layout.
#. Check the estimated waste. Click **Create Manufacturing Order**. The
   order becomes read-only and follows its production from then on.

Create orders from replenishment
--------------------------------

#. Open *Inventory > Operations > Replenishment > Laser Cutting
   Replenishment*. Only laser-cut products are listed.
#. Select the lines to restock and click **Create Laser Cutting Order**.
   One draft order is created per raw material. Every raw material unit
   is cut with the same layout, which is computed by weight as follows:

   * **Cover the demand**: the total output of every product reaches at
     least its quantity to order, rounded up to whole pieces.
   * **Fewest raw material units**: the quantity is the lowest one whose
     layout fits by weight on one unit.
   * **Least waste, most pieces**: the room left on each unit is filled
     with extra pieces of the selected products that have a quantity to
     order, choosing the combination that leaves the least waste and, for
     the same waste, cuts the most pieces. Those extra pieces go to stock
     on top of the quantity to order.
   * **Never negative waste**: the layout never claims more weight than
     one unit provides.

   The raw material needs a weight, and each product a consumption. When
   one piece of each selected product does not fit on a single unit of
   raw material, no order is created: select them in separate orders.
#. Adjust it to reality: set the real output per unit and quantity from
   the cutting layout, and split the order if several layouts are needed.
   One laser cutting order represents one layout.

Units of measure
================

Every quantity is handled either as a weight or as a piece count, so the
raw material and the finished products must be measured by weight or in
units (units, dozens, ...). Consumptions are always weights in the weight
unit of measure of the database: when the raw material line of a Bill of
Materials is measured in units of raw material (sheets, for instance), it
is turned into weight with the weight of the raw material. Creating a
manufacturing order from an order whose products use any other category
(area, length, volume) is blocked.

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

* Inael
* Ana Juaristi <anajuaristi@avanzosc.es>
* Lucía Echeverría <luciaecheverria@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.

License
-------

This module is licensed under the AGPL-3.0 or later. See the ``LICENSE``
file for the full license text.
