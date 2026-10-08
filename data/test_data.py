"""Massa de testes centralizada.

As credenciais do saucedemo são públicas (aparecem na própria tela de login),
mas a senha pode ser sobrescrita pela variável de ambiente SAUCE_PASSWORD,
seguindo a boa prática de não fixar segredos no código.
"""

import os
from dataclasses import dataclass

PASSWORD = os.getenv("SAUCE_PASSWORD", "secret_sauce")
TAX_RATE = 0.08


@dataclass(frozen=True)
class User:
    username: str
    password: str = PASSWORD


@dataclass(frozen=True)
class Customer:
    first_name: str
    last_name: str
    postal_code: str


STANDARD_USER = User("standard_user")
LOCKED_OUT_USER = User("locked_out_user")
PROBLEM_USER = User("problem_user")

DEFAULT_CUSTOMER = Customer("Luis", "Tapia", "69000-000")

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"
ONESIE = "Sauce Labs Onesie"

ALL_PRODUCTS = [
    "Sauce Labs Backpack",
    "Sauce Labs Bike Light",
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Fleece Jacket",
    "Sauce Labs Onesie",
    "Test.allTheThings() T-Shirt (Red)",
]


class Messages:
    USERNAME_REQUIRED = "Epic sadface: Username is required"
    PASSWORD_REQUIRED = "Epic sadface: Password is required"
    INVALID_CREDENTIALS = (
        "Epic sadface: Username and password do not match any user in this service"
    )
    LOCKED_OUT = "Epic sadface: Sorry, this user has been locked out."
    NOT_LOGGED_IN = "Epic sadface: You can only access '/inventory.html' when you are logged in."
    FIRST_NAME_REQUIRED = "Error: First Name is required"
    LAST_NAME_REQUIRED = "Error: Last Name is required"
    POSTAL_CODE_REQUIRED = "Error: Postal Code is required"
    ORDER_COMPLETE = "Thank you for your order!"
