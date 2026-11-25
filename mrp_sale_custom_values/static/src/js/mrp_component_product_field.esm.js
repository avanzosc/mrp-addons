import {Many2OneField, many2OneField} from "@web/views/fields/many2one/many2one_field";
import {registry} from "@web/core/registry";

export class MrpComponentProductField extends Many2OneField {
  get displayName() {
    const productName = super.displayName;
    const description = this.props.record.data.graphic_custom_description;
    if (this.props.readonly && description) {
      return `${productName} — ${description}`;
    }
    return productName;
  }
}

export const mrpComponentProductField = {
  ...many2OneField,
  component: MrpComponentProductField,
};

registry
  .category("fields")
  .add("mrp_component_product_many2one", mrpComponentProductField);
