# Copyright 2026 AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMrpProductConfigurator(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.attribute = cls.env["product.attribute"].create(
            {"name": "Test Attribute", "create_variant": "always"}
        )
        cls.value_1 = cls.env["product.attribute.value"].create(
            {"name": "Value 1", "attribute_id": cls.attribute.id}
        )
        cls.value_2 = cls.env["product.attribute.value"].create(
            {"name": "Value 2", "attribute_id": cls.attribute.id}
        )
        cls.configurable_product = cls.env["product.product"].create(
            {
                "name": "Configurable Product",
                "type": "consu",
                "is_storable": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [
                                Command.set([cls.value_1.id, cls.value_2.id])
                            ],
                        },
                    )
                ],
            }
        )
        cls.simple_product = cls.env["product.product"].create(
            {"name": "Simple Product", "type": "consu", "is_storable": True}
        )
        cls.pricelist_obj = cls.env["product.pricelist"]

    def _create_manufacturing_order(self, product, company=None):
        values = {"product_id": product.id, "product_qty": 1.0}
        if company:
            values["company_id"] = company.id
        return self.env["mrp.production"].create(values)

    def _create_company(self, name):
        company = self.env["res.company"].create({"name": name})
        self._archive_company_pricelists(company)
        return company

    def _create_company_pricelist(self, company, name=None):
        return self.pricelist_obj.create(
            {"name": name or company.name, "company_id": company.id}
        )

    def _archive_company_pricelists(self, company):
        self.pricelist_obj.search(
            ["|", ("company_id", "=", False), ("company_id", "=", company.id)]
        ).sudo().write({"active": False})

    def test_is_configurable_product_true(self):
        production = self._create_manufacturing_order(self.configurable_product)
        self.assertTrue(
            self.configurable_product.product_tmpl_id.has_configurable_attributes
        )
        self.assertTrue(production.is_configurable_product)

    def test_is_configurable_product_false(self):
        production = self._create_manufacturing_order(self.simple_product)
        self.assertFalse(
            self.simple_product.product_tmpl_id.has_configurable_attributes
        )
        self.assertFalse(production.is_configurable_product)

    def test_configurator_pricelist_from_production_company(self):
        company = self._create_company("Configurator Test Company")
        company_pricelist = self._create_company_pricelist(company)
        self.pricelist_obj.create({"name": "Shared Pricelist", "company_id": False})
        production = self._create_manufacturing_order(
            self.configurable_product, company=company
        )
        self.assertEqual(production.configurator_pricelist_id, company_pricelist)
        self.assertEqual(production.configurator_pricelist_id.company_id, company)
        self.assertEqual(
            production.configurator_currency_id, company_pricelist.currency_id
        )

    def test_configurator_pricelist_fallback_to_shared(self):
        company = self._create_company("Configurator Test Company No Pricelist")
        shared_pricelist = self.pricelist_obj.create(
            {"name": "Shared Pricelist", "company_id": False}
        )
        production = self._create_manufacturing_order(
            self.configurable_product, company=company
        )
        self.assertEqual(production.configurator_pricelist_id, shared_pricelist)
        self.assertEqual(
            production.configurator_currency_id, shared_pricelist.currency_id
        )

    def test_configurator_pricelist_recomputes_on_company_change(self):
        company_a = self._create_company("Configurator Company A")
        company_b = self._create_company("Configurator Company B")
        pricelist_a = self._create_company_pricelist(company_a)
        pricelist_b = self._create_company_pricelist(company_b)
        production = self._create_manufacturing_order(
            self.configurable_product, company=company_a
        )
        self.assertEqual(production.configurator_pricelist_id, pricelist_a)
        production.company_id = company_b
        self.assertEqual(production.configurator_pricelist_id, pricelist_b)
        self.assertEqual(production.configurator_currency_id, pricelist_b.currency_id)

    def test_configurator_pricelist_empty_without_pricelists(self):
        company = self._create_company("Configurator Test Company Empty")
        production = self._create_manufacturing_order(
            self.configurable_product, company=company
        )
        self.assertFalse(production.configurator_pricelist_id)
        self.assertFalse(production.configurator_currency_id)
