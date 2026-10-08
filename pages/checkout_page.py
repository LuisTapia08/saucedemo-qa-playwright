"""Páginas do fluxo de checkout: informações -> resumo -> confirmação."""

from __future__ import annotations

from playwright.sync_api import Page

from data.test_data import Customer
from pages.base_page import BasePage, parse_price


class CheckoutInformationPage(BasePage):
    path = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name_input = page.get_by_test_id("firstName")
        self.last_name_input = page.get_by_test_id("lastName")
        self.postal_code_input = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")
        self.error_message = page.get_by_test_id("error")

    @property
    def ready_indicator(self):
        return self.first_name_input

    def fill(self, first_name: str = "", last_name: str = "", postal_code: str = "") -> None:
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)

    def submit(self) -> None:
        self.continue_button.click()

    def continue_with(self, customer: Customer) -> CheckoutOverviewPage:
        self.fill(customer.first_name, customer.last_name, customer.postal_code)
        self.submit()
        return CheckoutOverviewPage(self.page).wait_until_loaded()

    def cancel(self):
        from pages.cart_page import CartPage

        self.cancel_button.click()
        return CartPage(self.page).wait_until_loaded()


class CheckoutOverviewPage(BasePage):
    path = "/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.subtotal_label = page.get_by_test_id("subtotal-label")
        self.tax_label = page.get_by_test_id("tax-label")
        self.total_label = page.get_by_test_id("total-label")
        self.finish_button = page.get_by_test_id("finish")
        self.cancel_button = page.get_by_test_id("cancel")

    @property
    def ready_indicator(self):
        return self.finish_button

    def product_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def product_prices(self) -> list[float]:
        return [parse_price(text) for text in self.item_prices.all_inner_texts()]

    def subtotal(self) -> float:
        return parse_price(self.subtotal_label.inner_text())

    def tax(self) -> float:
        return parse_price(self.tax_label.inner_text())

    def total(self) -> float:
        return parse_price(self.total_label.inner_text())

    def finish(self) -> CheckoutCompletePage:
        self.finish_button.click()
        return CheckoutCompletePage(self.page).wait_until_loaded()

    def cancel(self):
        from pages.inventory_page import InventoryPage

        self.cancel_button.click()
        return InventoryPage(self.page).wait_until_loaded()


class CheckoutCompletePage(BasePage):
    path = "/checkout-complete.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = page.get_by_test_id("complete-header")
        self.back_home_button = page.get_by_test_id("back-to-products")

    @property
    def ready_indicator(self):
        return self.header

    def back_home(self):
        from pages.inventory_page import InventoryPage

        self.back_home_button.click()
        return InventoryPage(self.page).wait_until_loaded()
