import re

import pytest
from playwright.sync_api import expect

from data.test_data import BACKPACK, BIKE_LIGHT, DEFAULT_CUSTOMER, TAX_RATE, Messages
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_complete_purchase_end_to_end(inventory_page: InventoryPage):
    expected_prices = [inventory_page.price_of(BACKPACK), inventory_page.price_of(BIKE_LIGHT)]
    cart = inventory_page.add_to_cart(BACKPACK, BIKE_LIGHT).go_to_cart()

    information = cart.checkout()
    expect(information.title).to_have_text("Checkout: Your Information")

    overview = information.continue_with(DEFAULT_CUSTOMER)
    expect(overview.title).to_have_text("Checkout: Overview")
    assert sorted(overview.product_names()) == sorted([BACKPACK, BIKE_LIGHT])

    subtotal = round(sum(expected_prices), 2)
    tax = round(subtotal * TAX_RATE, 2)
    assert overview.subtotal() == subtotal
    assert overview.tax() == tax
    assert overview.total() == round(subtotal + tax, 2)

    complete = overview.finish()
    expect(complete.page).to_have_url(re.compile(r"/checkout-complete\.html$"))
    expect(complete.header).to_have_text(Messages.ORDER_COMPLETE)
    expect(complete.cart_badge).to_be_hidden()


@pytest.mark.regression
def test_overview_item_total_equals_sum_of_items(cart_with_items: CartPage):
    overview = cart_with_items.checkout().continue_with(DEFAULT_CUSTOMER)

    assert overview.subtotal() == round(sum(overview.product_prices()), 2)


@pytest.mark.negative
@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "expected_error"),
    [
        pytest.param("", "", "", Messages.FIRST_NAME_REQUIRED, id="all-empty"),
        pytest.param("", "Tapia", "69000-000", Messages.FIRST_NAME_REQUIRED, id="missing-first"),
        pytest.param("Luis", "", "69000-000", Messages.LAST_NAME_REQUIRED, id="missing-last"),
        pytest.param("Luis", "Tapia", "", Messages.POSTAL_CODE_REQUIRED, id="missing-postal"),
    ],
)
def test_checkout_information_is_required(
    cart_with_items: CartPage,
    first_name: str,
    last_name: str,
    postal_code: str,
    expected_error: str,
):
    information = cart_with_items.checkout()

    information.fill(first_name, last_name, postal_code)
    information.submit()

    expect(information.error_message).to_have_text(expected_error)
    expect(information.page).to_have_url(re.compile(r"/checkout-step-one\.html$"))


@pytest.mark.regression
def test_cancel_on_information_returns_to_cart(cart_with_items: CartPage):
    cart = cart_with_items.checkout().cancel()

    expect(cart.title).to_have_text("Your Cart")
    expect(cart.items).to_have_count(2)


@pytest.mark.regression
def test_cancel_on_overview_keeps_cart(cart_with_items: CartPage):
    inventory = cart_with_items.checkout().continue_with(DEFAULT_CUSTOMER).cancel()

    expect(inventory.title).to_have_text("Products")
    expect(inventory.cart_badge).to_have_text("2")


@pytest.mark.regression
def test_back_home_after_order(cart_with_items: CartPage):
    complete = cart_with_items.checkout().continue_with(DEFAULT_CUSTOMER).finish()

    inventory = complete.back_home()

    expect(inventory.title).to_have_text("Products")
    expect(inventory.cart_badge).to_be_hidden()


@pytest.mark.known_bug
@pytest.mark.xfail(
    reason="BUG-001: o sistema permite iniciar o checkout com o carrinho vazio "
    "e conclui um pedido de $0.00 (ver docs/bug-reports.md)",
)
def test_checkout_is_blocked_with_empty_cart(inventory_page: InventoryPage):
    cart = inventory_page.go_to_cart()
    expect(cart.items).to_have_count(0)

    cart.checkout_button.click()

    expect(cart.page).to_have_url(re.compile(r"/cart\.html$"), timeout=2_000)
