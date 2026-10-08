from playwright.sync_api import Page

from pages.base_page import BasePage, parse_price


class ProductPage(BasePage):
    path = "/inventory-item.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.name = page.get_by_test_id("inventory-item-name")
        self.description = page.get_by_test_id("inventory-item-desc")
        self.price_label = page.get_by_test_id("inventory-item-price")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")
        self.remove_button = page.get_by_test_id("remove")
        self.back_button = page.get_by_test_id("back-to-products")

    @property
    def ready_indicator(self):
        return self.back_button

    def price(self) -> float:
        return parse_price(self.price_label.inner_text())

    def add_to_cart(self) -> "ProductPage":
        self.add_to_cart_button.click()
        return self

    def back_to_products(self):
        from pages.inventory_page import InventoryPage

        self.back_button.click()
        return InventoryPage(self.page).wait_until_loaded()
