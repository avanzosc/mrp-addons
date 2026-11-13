.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
MRP BoM Attribute Match Manual
===================================

This module makes the ``Match on Attributes`` field editable on BoM component
lines provided by ``mrp_bom_attribute_match``.

It also adds a ``Component Match Attributes`` field to map parent product
attributes to different component attributes. For example, a skateboard can use
``M2`` as the parent attribute while the component template uses ``Color`` or
``Size``. When manufacturing a variant with ``M2 = Red``, the module searches
for a component variant with a selected component attribute value named ``Red``.

The module also allows component templates to contain attributes that are not
present on the manufactured product, as those attributes can be mapped manually.

Manufacturing order component lines show the source BoM block. Components from
an exploded kit display that kit, while direct dynamic components display their
configured component template.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported.

Credits
=======

Authors
-------

* AvanzOSC

Contributors
------------

* Ane Gurruchaga <aneavanzosc@gmail.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
