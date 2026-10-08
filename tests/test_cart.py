import pytest
from playwright.sync_api import expect

from data.test_data import BACKPACK, BIKE_LIGHT, ONESIE
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_add_single_product_to_cart(inventory_page: InventoryPage):
    inventory_page.add_to_cart(BACKPACK)

    expect(inventory_page.cart_badge).to_have_text("1")
    expect(inventory_page.remove_button(BACKPACK)).to_be_visible()


@pytest.mark.regression
def test_add_multiple_products_to_cart(inventory_page: InventoryPage):
    inventory_page.add_to_cart(BACKPACK, BIKE_LIGHT, ONESIE)
    expect(inventory_page.cart_badge).to_have_text("3")

    cart = inventory_page.go_to_cart()

    expect(cart.title).to_have_text("Your Cart")
    assert sorted(cart.product_names()) == sorted([BACKPACK, BIKE_LIGHT, ONESIE])


@pytest.mark.regression
def test_add_to_cart_from_product_details(inventory_page: InventoryPage):
    product = inventory_page.open_product(ONESIE).add_to_cart()

    expect(product.cart_badge).to_have_text("1")
    expect(product.remove_button).to_be_visible()


@pytest.mark.regression
def test_remove_product_from_inventory_page(inventory_page: InventoryPage):
    inventory_page.add_to_cart(BACKPACK)

    inventory_page.remove_from_cart(BACKPACK)

    expect(inventory_page.cart_badge).to_be_hidden()
    expect(inventory_page.add_to_cart_button(BACKPACK)).to_be_visible()


@pytest.mark.regression
def test_remove_product_from_cart_page(cart_with_items: CartPage):
    cart_with_items.remove(BACKPACK)

    expect(cart_with_items.items).to_have_count(1)
    expect(cart_with_items.item(BIKE_LIGHT)).to_be_visible()
    expect(cart_with_items.cart_badge).to_have_text("1")


@pytest.mark.regression
def test_cart_persists_when_continuing_shopping(cart_with_items: CartPage):
    inventory = cart_with_items.continue_shopping()

    expect(inventory.cart_badge).to_have_text("2")
    assert sorted(inventory.go_to_cart().product_names()) == sorted([BACKPACK, BIKE_LIGHT])


@pytest.mark.regression
def test_cart_persists_after_page_reload(inventory_page: InventoryPage):
    inventory_page.add_to_cart(BACKPACK)

    inventory_page.page.reload()

    expect(inventory_page.cart_badge).to_have_text("1")


@pytest.mark.regression
def test_reset_app_state_empties_cart(inventory_page: InventoryPage):
    inventory_page.add_to_cart(BACKPACK, BIKE_LIGHT)

    inventory_page.reset_app_state()

    expect(inventory_page.cart_badge).to_be_hidden()
    expect(inventory_page.go_to_cart().items).to_have_count(0)


@pytest.mark.known_bug
@pytest.mark.xfail(
    reason="BUG-002: após 'Reset App State' o botão continua como 'Remove' "
    "mesmo com o carrinho vazio (ver docs/bug-reports.md)",
)
def test_reset_app_state_restores_add_buttons(inventory_page: InventoryPage):
    inventory_page.add_to_cart(BACKPACK)

    inventory_page.reset_app_state()

    expect(inventory_page.add_to_cart_button(BACKPACK)).to_be_visible(timeout=2_000)
