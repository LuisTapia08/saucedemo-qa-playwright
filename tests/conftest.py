import base64

import pytest
from playwright.sync_api import Page, Playwright

from data.test_data import BACKPACK, BIKE_LIGHT, STANDARD_USER
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture(scope="session", autouse=True)
def configure_test_id(playwright: Playwright) -> None:
    """O saucedemo usa `data-test` (e não `data-testid`) nos elementos."""
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page).open()


@pytest.fixture
def inventory_page(login_page: LoginPage) -> InventoryPage:
    """Usuário padrão já autenticado na vitrine de produtos."""
    return login_page.login_as(STANDARD_USER)


@pytest.fixture
def cart_with_items(inventory_page: InventoryPage) -> CartPage:
    """Carrinho com dois produtos, pronto para o checkout."""
    return inventory_page.add_to_cart(BACKPACK, BIKE_LIGHT).go_to_cart()


# --- Relatório HTML -------------------------------------------------------


def pytest_html_report_title(report):
    report.title = "Saucedemo – Relatório de Testes E2E"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Anexa um screenshot da página ao relatório HTML quando um teste falha."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page = item.funcargs.get("page")
    if page is None or page.is_closed():
        return
    try:
        import pytest_html

        png = page.screenshot(full_page=True)
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.png(base64.b64encode(png).decode(), "Screenshot"))
        extras.append(pytest_html.extras.url(page.url, "URL no momento da falha"))
        report.extras = extras
    except Exception:  # nunca deixar o relatório derrubar a execução
        pass
