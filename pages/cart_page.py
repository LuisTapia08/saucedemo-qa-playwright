from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage, exact_text

if TYPE_CHECKING:
    from pages.checkout_page import CheckoutInformationPage
    from pages.inventory_page import InventoryPage


class CartPage(BasePage):
    path = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    @property
    def ready_indicator(self) -> Locator:
        return self.checkout_button

    def item(self, name: str) -> Locator:
        return self.items.filter(
            has=self.page.get_by_test_id("inventory-item-name").filter(has_text=exact_text(name))
        )

    def product_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def remove(self, name: str) -> CartPage:
        self.item(name).get_by_role("button", name="Remove").click()
        return self

    def checkout(self) -> CheckoutInformationPage:
        from pages.checkout_page import CheckoutInformationPage

        self.checkout_button.click()
        return CheckoutInformationPage(self.page).wait_until_loaded()

    def continue_shopping(self) -> InventoryPage:
        from pages.inventory_page import InventoryPage

        self.continue_shopping_button.click()
        return InventoryPage(self.page).wait_until_loaded()
