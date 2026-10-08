from __future__ import annotations

import re
from typing import TYPE_CHECKING

from playwright.sync_api import Locator, Page, expect

if TYPE_CHECKING:
    from pages.cart_page import CartPage
    from pages.login_page import LoginPage


def parse_price(text: str) -> float:
    """Extrai o valor numérico de textos como '$29.99' ou 'Total: $43.18'."""
    match = re.search(r"\$(\d+(?:\.\d{2})?)", text)
    if not match:
        raise ValueError(f"Nenhum preço encontrado em: {text!r}")
    return float(match.group(1))


def exact_text(text: str) -> re.Pattern[str]:
    """Regex de correspondência exata (ignorando espaços nas bordas)."""
    return re.compile(rf"^\s*{re.escape(text)}\s*$")


class BasePage:
    """Elementos e ações comuns a todas as páginas autenticadas."""

    path = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.title = page.get_by_test_id("title")
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.menu_button = page.locator("#react-burger-menu-btn")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")
        self.reset_app_link = page.get_by_test_id("reset-sidebar-link")
        self.close_menu_button = page.locator("#react-burger-cross-btn")

    @property
    def ready_indicator(self) -> Locator:
        """Elemento que só existe quando esta página terminou de carregar."""
        return self.title

    def open(self):
        self.page.goto(self.path)
        return self

    def wait_until_loaded(self):
        """Garante que a navegação terminou antes de interagir com a nova página.

        Evita que um locator resolva elementos da página anterior durante a transição.
        """
        expect(self.ready_indicator).to_be_visible()
        return self

    def cart_count(self) -> int:
        if self.cart_badge.count() == 0:
            return 0
        return int(self.cart_badge.inner_text())

    def go_to_cart(self) -> CartPage:
        from pages.cart_page import CartPage

        self.cart_link.click()
        return CartPage(self.page).wait_until_loaded()

    def open_menu(self) -> None:
        self.menu_button.click()

    def logout(self) -> LoginPage:
        from pages.login_page import LoginPage

        self.open_menu()
        self.logout_link.click()
        return LoginPage(self.page).wait_until_loaded()

    def reset_app_state(self) -> None:
        self.open_menu()
        self.reset_app_link.click()
        self.close_menu_button.click()
