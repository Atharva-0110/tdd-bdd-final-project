# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, DataValidationError, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""

        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )

        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_update_product_without_id(self):
        """Update without an ID should raise a validation error"""
        product = ProductFactory()
        product.id = None

        with self.assertRaises(DataValidationError):
            product.update()

    def test_deserialize_invalid_availability(self):
        """It should reject a non-boolean availability value"""
        data = ProductFactory().serialize()
        data["available"] = "yes"

        with self.assertRaises(DataValidationError):
            Product().deserialize(data)

    def test_deserialize_invalid_category(self):
        """It should reject an unknown category"""
        data = ProductFactory().serialize()
        data["category"] = "INVALID_CATEGORY"

        with self.assertRaises(DataValidationError):
            Product().deserialize(data)

    def test_deserialize_missing_name(self):
        """It should reject a product with a missing name"""
        data = ProductFactory().serialize()
        del data["name"]

        with self.assertRaises(DataValidationError):
            Product().deserialize(data)

    def test_deserialize_empty_body(self):
        """It should reject an empty product body"""
        with self.assertRaises(DataValidationError):
            Product().deserialize(None)

    def test_find_by_name(self):
        """It should find products by name"""
        product = ProductFactory(name="Test Fedora")
        product.create()

        result = Product.find_by_name("Test Fedora").all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Test Fedora")

    def test_find_by_price(self):
        """It should find products by price"""
        product = ProductFactory(price=Decimal("25.50"))
        product.create()

        result = Product.find_by_price("25.50").all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, product.name)

    def test_find_by_availability(self):
        """It should find available products"""
        product = ProductFactory(available=True)
        product.create()

        result = Product.find_by_availability(True).all()
        self.assertTrue(any(item.id == product.id for item in result))

    def test_find_by_category(self):
        """It should find products by category"""
        product = ProductFactory(category=Category.CLOTHS)
        product.create()

        result = Product.find_by_category(Category.CLOTHS).all()
        self.assertTrue(any(item.id == product.id for item in result))
