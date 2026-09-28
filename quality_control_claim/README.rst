.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Quality Control Claim
=====================

This module integrates the **Quality Control** workflow with the **CRM Claims**
system in Odoo. It allows claims to be generated automatically when a quality
inspection fails, either at the overall inspection level or at the individual
test line level, reducing manual work and ensuring that quality issues are
always tracked and followed up.

Features
========

Automatic claim on inspection failure
--------------------------------------

A new boolean field **Automatic Claims** is added to both the *QC Test* and
the *QC Inspection* objects.

When this option is enabled on a test, every inspection generated from that
test will inherit the setting. If the inspection is approved and its final
status is **"Quality failed"**, a claim is created automatically with:

* A descriptive name referencing the inspection name and, if applicable, the
  inspected object.
* The current date and time as the claim date.
* A reference back to the originating QC inspection (``model_ref_id``), so the
  claim is always traceable to its source.

Automatic claim per failed line
---------------------------------

A second boolean field **Automatic Claims by Line** is also added to both
*QC Test* and *QC Inspection*.

When this option is enabled, instead of a single claim for the whole
inspection, **one individual claim is created for each test line whose status
is "No ok"**. Each claim includes:

* The inspection name, the inspected object (if any), and the specific line
  name, so the exact failure point is immediately identifiable.
* The same date and ``model_ref_id`` traceability as the global claim.

.. note::
   The two options are independent. You may enable *Automatic Claims* for a
   global summary claim, *Automatic Claims by Line* for granular tracking, or
   both simultaneously.

Claims smart button on inspections
------------------------------------

A **Claims** stat button is displayed directly on each QC inspection form view.
It shows the total number of claims linked to that inspection and provides
one-click navigation to the list of those claims.

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <ajuaristio@gmail.com>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Daniel Campos <danielcampos@avanzosc.es>
* Lucía Echeverría <luciaecheverria@avanzosc.es>
