# Copyright 2016-19 ForgeFlow S.L.
# Copyright 2016-19 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseRequestOperatingUnit(TransactionCase):
    def setUp(self):
        super().setUp()
        # Models
        self.res_users_model = self.env["res.users"]
        self.purchase_request = self.env["purchase.request"]
        self.purchase_request_line = self.env["purchase.request.line"]
        # Company
        self.company = self.env.ref("base.main_company")
        self.company2 = self.env["res.company"].create({"name": "Test Company"})
        # Main Operating Unit
        self.ou1 = self.env.ref("operating_unit.main_operating_unit")
        # B2C Operating Unit
        self.b2c = self.env.ref("operating_unit.b2c_operating_unit")
        # Product
        self.product1 = self.env.ref("product.product_product_7")
        self.product_uom = self.env.ref("uom.product_uom_unit")
        # User
        self.user_root = self.env.ref("base.user_root")
        # Groups
        self.grp_pr_mngr = self.env.ref(
            "purchase_request.group_purchase_request_manager"
        )
        # Picking Type
        b2c_wh = self.env.ref("stock_operating_unit.stock_warehouse_b2c")
        self.b2c_type_in = b2c_wh.in_type_id
        self.picking_type = self.env.ref("stock.picking_type_in")

        # Creates Users and Purchase request
        self.user1 = self._create_user("user_1", [], self.company, [self.ou1])
        self.user2 = self._create_user(
            "user_2", self.grp_pr_mngr, self.company, [self.b2c]
        )
        self.request1 = self._create_purchase_request(self.ou1)
        self._purchase_line(self.request1)
        self.request2 = self._create_purchase_request(self.b2c, self.b2c_type_in.id)
        self._purchase_line(self.request2)

    def _create_user(self, login, groups, company, operating_units, context=None):
        """Create a user."""
        group_ids = [group.id for group in groups]
        user = self.res_users_model.create(
            {
                "name": "Test Purchase Request User",
                "login": login,
                "password": "demo",
                "email": "example@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "operating_unit_ids": [(4, ou.id) for ou in operating_units],
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user

    def _purchase_line(self, request):
        line = self.purchase_request_line.create(
            {
                "request_id": request.id,
                "product_id": self.product1.id,
                "product_uom_id": self.product_uom.id,
                "product_qty": 5.0,
            }
        )
        return line

    def _create_purchase_request(self, operating_unit, picking_type_id=False):
        purchase_request = self.purchase_request.create(
            {
                "assigned_to": self.user_root.id,
                "picking_type_id": picking_type_id or self.picking_type.id,
                "operating_unit_id": operating_unit.id,
            }
        )
        return purchase_request

    def test_purchase_request(self):
        record = self.purchase_request.with_user(self.user2.id).search(
            [("id", "=", self.request1.id), ("operating_unit_id", "=", self.ou1.id)]
        )
        self.assertEqual(
            record.ids, [], "User 2 should not have access to OU %s" % self.ou1.name
        )

        # Check company in OU and operating unit must be equal
        with self.assertRaises(ValidationError):
            with Form(self.request1) as pr:
                pr.company_id = self.company2

        # Check OU in picking type and operating unit must be equal
        with self.assertRaises(ValidationError):
            with Form(self.request1) as pr:
                pr.picking_type_id = self.b2c_type_in

        # Check OU in assigned_to and operating unit must be equal
        with self.assertRaises(ValidationError):
            with Form(self.request1) as pr:
                pr.assigned_to = self.user2
                pr.operating_unit_id = self.ou1
