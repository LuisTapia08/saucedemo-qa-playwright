import re

import pytest
from playwright.sync_api import expect

from data.test_data import ALL_PRODUCTS, BACKPACK
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_inventory_shows_all_products(inventory_page: InventoryPage):
    expect(inventory_page.items).to_have_count(len(ALL_PRODUCTS))
    assert sorted(inventory_page.product_names()) == sorted(ALL_PRODUCTS)


@pytest.mark.regression
def test_every_product_has_a_positive_price(inventory_page: InventoryPage):
    prices = inventory_page.product_prices()

    assert len(prices) == len(ALL_PRODUCTS)
    assert all(price > 0 for price in prices)


@pytest.mark.regression
def test_default_sort_is_name_ascending(inventory_page: InventoryPage):
    names = inventory_page.product_names()
    assert names == sorted(names)


@pytest.mark.regression
@pytest.mark.parametrize(
    ("option", "key", "reverse"),
    [
        pytest.param("az", "name", False, id="name-a-to-z"),
        pytest.param("za", "name", True, id="name-z-to-a"),
        pytest.param("lohi", "price", False, id="price-low-to-high"),
        pytest.param("hilo", "price", True, id="price-high-to-low"),
    ],
)
def test_sort_products(inventory_page: InventoryPage, option: str, key: str, reverse: bool):
    inventory_page.sort_by(option)

    values = inventory_page.product_names() if key == "name" else inventory_page.product_prices()
    assert values == sorted(values, reverse=reverse)


@pytest.mark.regression
def test_product_details_match_listing(inventory_page: InventoryPage):
    listed_price = inventory_page.price_of(BACKPACK)

    product = inventory_page.open_product(BACKPACK)

    expect(product.page).to_have_url(re.compile(r"/inventory-item\.html\?id=\d+"))
    expect(product.name).to_have_text(BACKPACK)
    assert product.price() == listed_price


@pytest.mark.regression
def test_back_from_product_details(inventory_page: InventoryPage):
    inventory = inventory_page.open_product(BACKPACK).back_to_products()

    expect(inventory.title).to_have_text("Products")
    expect(inventory.items).to_have_count(len(ALL_PRODUCTS))
