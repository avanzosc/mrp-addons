/* @odoo-module */

import {Many2OneField, many2OneField} from "@web/views/fields/many2one/many2one_field";
import {ProductConfiguratorDialog} from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import {registry} from "@web/core/registry";
import {serializeDateTime} from "@web/core/l10n/dates";

const {DateTime} = luxon;

class MrpProductConfiguratorDialog extends ProductConfiguratorDialog {
  _checkExclusions(product) {
    if (product.exclusions) {
      for (const ptavId of this._getCombination(product)) {
        product.exclusions[ptavId] ||= [];
      }
    }
    return super._checkExclusions(product);
  }
}

export class MrpProductField extends Many2OneField {
  static template = "mrp_product_configurator.MrpProductField";

  get hasConfigurationButton() {
    return Boolean(
      this.props.record.data.product_id &&
        this.props.record.data.is_configurable_product
    );
  }

  async onEditConfiguration() {
    const production = this.props.record.data;
    const ptavIds = production.product_variant_attributes.records.map(
      (record) => record.resId
    );

    this.dialog.add(MrpProductConfiguratorDialog, {
      productTemplateId: production.product_tmpl_id[0],
      ptavIds,
      customPtavs: [],
      quantity: production.product_qty,
      productUOMId: production.product_uom_id[0],
      companyId: production.company_id[0],
      pricelistId: production.configurator_pricelist_id[0],
      currencyId: production.configurator_currency_id[0],
      soDate: serializeDateTime(DateTime.now()),
      edit: true,
      save: async (product) => {
        await this.props.record.update({
          product_id: [product.id, product.display_name],
        });
      },
      discard: () => null,
    });
  }
}

export const mrpProductField = {
  ...many2OneField,
  component: MrpProductField,
};

registry.category("fields").add("mrp_product_many2one", mrpProductField);
