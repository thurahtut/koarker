# Copyright 2016-19 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class HrContract(models.Model):

    _inherit = "hr.contract"

    operating_unit_id = fields.Many2one(
        "operating.unit",
        "Operating Unit",
        default=lambda self: self.env["res.users"].operating_unit_default_get(
            self._uid
        ),
        domain=lambda self: [
            (
                "id",
                "in",
                [
                    operating_unit.id
                    for operating_unit in self.env.user.operating_unit_ids
                ],
            )
        ],
    )
