import base64
from io import BytesIO

import qrcode

from odoo import models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def _create_qr_code(self, integer_to_convert):
        if integer_to_convert:
            sequence_str = str(integer_to_convert)

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(sequence_str)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

            return qr_image
        else:
            return False
