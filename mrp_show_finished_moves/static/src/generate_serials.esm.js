// @odoo-module
import {onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";

const generateSerialsEntry = registry
  .category("view_widgets")
  .get("generate_serials", null);

if (generateSerialsEntry) {
  patch(generateSerialsEntry.component.prototype, {
    openDialog(ev) {
      const ctx = this.props.record.context || {};
      const {mo_next_serial: nextSerial, mo_product_qty: productQty} = ctx;

      if (nextSerial === undefined && productQty === undefined) {
        return super.openDialog(ev);
      }

      const originalAdd = this.dialog.add.bind(this.dialog);
      this.dialog.add = (DialogComponent, props, options) => {
        this.dialog.add = originalAdd;

        const OrigSetup = DialogComponent.prototype.setup;

        class MOGenerateDialog extends DialogComponent {
          setup() {
            OrigSetup.call(this);
            onMounted(() => {
              if (this.props.mode !== "generate") return;
              if (nextSerial && this.nextSerial?.el)
                this.nextSerial.el.value = nextSerial;
              if (productQty !== undefined && this.nextSerialCount?.el)
                this.nextSerialCount.el.value = Math.floor(productQty);
              if (this.keepLines?.el) this.keepLines.el.checked = false;
            });
          }
        }

        MOGenerateDialog.template = DialogComponent.template;
        MOGenerateDialog.components = DialogComponent.components;
        MOGenerateDialog.props = DialogComponent.props;

        return originalAdd(MOGenerateDialog, props, options);
      };

      super.openDialog(ev);
    },
  });
}
