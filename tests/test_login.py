import re

import pytest
from playwright.sync_api import Page, expect

from data.test_data import LOCKED_OUT_USER, PASSWORD, STANDARD_USER, Messages
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_with_valid_credentials(login_page: LoginPage):
    inventory = login_page.login_as(STANDARD_USER)

    expect(inventory.page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(inventory.title).to_have_text("Products")


@pytest.mark.negative
@pytest.mark.parametrize(
    ("username", "password", "expected_error"),
    [
        pytest.param("", "", Messages.USERNAME_REQUIRED, id="empty-fields"),
        pytest.param("", PASSWORD, Messages.USERNAME_REQUIRED, id="missing-username"),
        pytest.param("standard_user", "", Messages.PASSWORD_REQUIRED, id="missing-password"),
        pytest.param("standard_user", "wrong", Messages.INVALID_CREDENTIALS, id="wrong-password"),
        pytest.param("ghost_user", PASSWORD, Messages.INVALID_CREDENTIALS, id="unknown-user"),
        pytest.param(
            "STANDARD_USER", PASSWORD, Messages.INVALID_CREDENTIALS, id="username-case-sensitive"
        ),
        pytest.param(
            LOCKED_OUT_USER.username, LOCKED_OUT_USER.password, Messages.LOCKED_OUT, id="locked-out"
        ),
    ],
)
def test_login_fails_with_invalid_input(
    login_page: LoginPage, username: str, password: str, expected_error: str
):
    login_page.login(username, password)

    expect(login_page.error_message).to_have_text(expected_error)
    expect(login_page.page).not_to_have_url(re.compile(r"/inventory\.html"))


@pytest.mark.negative
def test_error_message_can_be_dismissed(login_page: LoginPage):
    login_page.login("", "")
    expect(login_page.error_message).to_be_visible()

    login_page.dismiss_error()

    expect(login_page.error_message).to_be_hidden()


@pytest.mark.regression
def test_password_field_is_masked(login_page: LoginPage):
    expect(login_page.password_input).to_have_attribute("type", "password")


@pytest.mark.negative
def test_inventory_requires_authentication(page: Page):
    InventoryPage(page).open()

    login = LoginPage(page)
    expect(login.error_message).to_have_text(Messages.NOT_LOGGED_IN)
    expect(login.login_button).to_be_visible()


@pytest.mark.smoke
def test_logout_returns_to_login(inventory_page: InventoryPage):
    login = inventory_page.logout()

    expect(login.login_button).to_be_visible()
    expect(login.username_input).to_be_empty()


@pytest.mark.negative
def test_session_is_invalidated_after_logout(inventory_page: InventoryPage):
    login = inventory_page.logout()

    InventoryPage(login.page).open()

    expect(login.error_message).to_have_text(Messages.NOT_LOGGED_IN)
