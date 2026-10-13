# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.

"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from service.models import Product, Category


class ProductFactory(factory.Factory):
    """Creates fake products for testing"""

    class Meta:
        """Maps factory to data model"""
        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    description = factory.Faker("text")
    price = FuzzyDecimal(0.5, 1000.0, precision=2)
    available = factory.Faker("boolean")
    category = FuzzyChoice(list(Category))
