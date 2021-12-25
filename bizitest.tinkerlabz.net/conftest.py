import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import time
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def pytest_addoption(parser):
    parser.addoption('--url', help='Set a URL adress for testing', type=str, default='https://bizitest.tinkerlabz.net/')
    parser.addoption('--browser', help='browser Chrome / Firefox', type=str, default='Firefox')
    parser.addoption('--search', help='Searching query', type=str, default='top')
    parser.addoption('--coupon', help='enter coupon', type=str)
    parser.addoption('--captcha-cookie-name', help='cookie-name', type=str, default='E2ETEST')

@pytest.fixture(scope="module")
def set_browser(request):

    browser = request.config.getoption('--browser')
    url = request.config.getoption('--url')
    search = request.config.getoption('--search')
    coupon = request.config.getoption('--coupon')
    cookie = request.config.getoption('--captcha-cookie-name')
    return browser, url, search, coupon, cookie




""" Gmail credentials
email bizibitesting@gmail.com
pwd b1z1t3st1ng
"""
