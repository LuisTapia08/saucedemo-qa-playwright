from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage, exact_text, parse_price

if TYPE_CHECKING:
    from pages.product_page import ProductPage

SortOption = Literal["az", "za", "lohi", "hilo"]


class InventoryPage(BasePage):
    path = "/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.sort_select = page.get_by_test_id("product-sort-container")

    @property
    def ready_indicator(self) -> Locator:
        return self.sort_select

    def item(self, name: str) -> Locator:
        """Card do produto, localizado pelo nome exato."""
        return self.items.filter(
            has=self.page.get_by_test_id("inventory-item-name").filter(has_text=exact_text(name))
        )

    def add_to_cart_button(self, name: str) -> Locator:
        return self.item(name).get_by_role("button", name="Add to cart")

    def remove_button(self, name: str) -> Locator:
        return self.item(name).get_by_role("button", name="Remove")

    def add_to_cart(self, *names: str) -> InventoryPage:
        for name in names:
            self.add_to_cart_button(name).click()
        return self

    def remove_from_cart(self, name: str) -> InventoryPage:
        self.remove_button(name).click()
        return self

    def sort_by(self, option: SortOption) -> InventoryPage:
        self.sort_select.select_option(option)
        return self

    def product_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def product_prices(self) -> list[float]:
        return [parse_price(text) for text in self.item_prices.all_inner_texts()]

    def price_of(self, name: str) -> float:
        return parse_price(self.item(name).get_by_test_id("inventory-item-price").inner_text())

    def open_product(self, name: str) -> ProductPage:
        from pages.product_page import ProductPage

        self.item_names.filter(has_text=exact_text(name)).click()
        return ProductPage(self.page).wait_until_loaded()
