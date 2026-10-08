from playwright.sync_api import Page

from data.test_data import User
from pages.base_page import BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input = page.get_by_test_id("username")
        self.password_input = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error_message = page.get_by_test_id("error")
        self.error_close_button = page.get_by_test_id("error-button")

    @property
    def ready_indicator(self):
        return self.login_button

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def login_as(self, user: User) -> InventoryPage:
        self.login(user.username, user.password)
        return InventoryPage(self.page).wait_until_loaded()

    def dismiss_error(self) -> None:
        self.error_close_button.click()
