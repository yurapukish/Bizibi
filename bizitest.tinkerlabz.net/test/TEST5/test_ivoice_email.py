import sys
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ecommtester.bizisite import BizisiteBuyer
from ecommtester.vendor import Vendor
from test.get_arguments import get_params, get_filepath

data = get_params()


def test_ivoice_email():
    try:
        browser, url, vendor_username, vendor_password, filename = data['BROWSER_FIREFOX'], data['URL'], \
                                                         data['TEST_VENDOR_USERNAME'], data['TEST_VENDOR_PASSWORD'], data['FILE_PATH']
        filename = get_filepath(filename)
        vendor = Vendor(browser, url)
        driver = vendor.get_driver()
        vendor.login_as_user(vendor_username, vendor_password)

        invoice_number, invoice_data = vendor.invoice_form(filename)
        result = vendor.check_invoice_data(invoice_number, invoice_data)
        assert result == True, "Problem in invoice"

        # open gmail
        vendor.terminate_browser()
        del vendor

        USER = BizisiteBuyer(browser, url)
        driver = USER.get_driver()
        USER.open_Gmail_and_open_letter()

        # open link
        link = USER.wait_for_el((By.CSS_SELECTOR, 'div:nth-child(2)>p:nth-child(5)>a'))
        link.click()

        # switch page
        driver.switch_to.window(driver.window_handles[1])

        USER.checkout(invoice=True)
        USER.terminate_browser()
        del USER

        # create vendor
        vendor = Vendor(browser, url)
        driver = vendor.get_driver()
        vendor.login_as_user(vendor_username, vendor_password)

        # open orders
        order = vendor.wait_for_el((By.CLASS_NAME, 'home-warning-text'))
        order.click()

        # find approved
        approved = vendor.wait_for_el((By.CLASS_NAME, 'green-back'))
        approved.click()

        # status  not Payment Pending
        order_number = vendor.wait_for_el((By.CSS_SELECTOR, 'tr:nth-child(1)>td:nth-child(1)'))
        assert order_number.text == invoice_number, "Order_number != invoice_number"
        status = vendor.wait_for_el((By.CSS_SELECTOR, 'td:nth-child(7)'))
        assert status.text == "Paid", "Order status is not Approved"
    finally:
        driver.quit()
