from datetime import *
from time import *
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ecommtester.bizisite import BizisiteBuyer
from test.get_arguments import get_params, get_filepath
from ecommtester.vendor import Vendor

data = get_params()


def test_second_ivoice_email():
    try:
        browser, url, vendor_username, vendor_password, search_query = data['BROWSER_FIREFOX'], data['URL'], \
                                                                       data['TEST_VENDOR_USERNAME'], data[
                                                                           'TEST_VENDOR_PASSWORD'], data['SEARCH']
        image1, image2, image3 = get_filepath(data['IMAGES']['IMAGE1']), get_filepath(
            data['IMAGES']['IMAGE2']), get_filepath(data['IMAGES']['IMAGE3'])
        vendor = Vendor(browser, url, vendor_username, vendor_password)
        driver = vendor.get_driver()
        login = vendor.login_as_user(vendor_username, vendor_password)
        print("login", login)
        assert login == True, "Login FAiled"
        vendor.modify_image()
        time.sleep(12)
    finally:
        driver.quit()
