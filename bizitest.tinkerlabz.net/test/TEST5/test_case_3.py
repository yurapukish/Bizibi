import sys
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
    global vendor
    try:
        browser, url, vendor_username, vendor_password, search_query, filename = data['BROWSER_FIREFOX'], data['URL'], \
                                                                                 data['TEST_VENDOR_USERNAME'], data[
                                                                                     'TEST_VENDOR_PASSWORD'], data[
                                                                                     'SEARCH'], data['FILE_PATH']
        filename = get_filepath(filename)
        vendor = Vendor(browser, url)
        driver = vendor.get_driver()

        vendor.login_as_user(vendor_username, vendor_password)

        # create 1 invoice
        invoice_number, invoice_data = vendor.invoice_form(filename)
        result = vendor.check_invoice_data(invoice_number, invoice_data)
        assert result == True, "Problem in invoice"

        # go to orders and check that only 1 product is in the order
        # go to orders
        orders = vendor.wait_for_el((By.LINK_TEXT, "Orders"))
        orders.click()
        view_button = vendor.wait_for_el((By.TAG_NAME, 'button'))
        view_button.click()
        # count number of rows
        rows = WebDriverWait(driver, vendor.DEFAULT_WAIT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#orderDetailRows>tr"))
        )
        assert len(rows) == 9, "In orders more that 1 elements"

        # add item into vendors card
        # search_product & add 1 product to card
        go_to_main_site = vendor.wait_for_el((By.LINK_TEXT, 'Main Site'))
        go_to_main_site.click()

        driver.find_element(By.CSS_SELECTOR, '[name="search_by"]').send_keys(search_query)
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'submitButton')))
        element.click()

        first_product = driver.find_element(By.CLASS_NAME, 'list-product-item-action')
        first_product.click()
        time.sleep(vendor.TIME)
        items_on_card = vendor.count_items_in_card()
        assert items_on_card == 1, "Items is on the vendors card"

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

        vendor = Vendor(browser, url)
        driver = vendor.get_driver()
        vendor.login_as_user(vendor_username, vendor_password)
        # VENDOR
        # 2 create invoice
        invoice_number_2, invoice_data_2 = vendor.invoice_form(filename)
        result = vendor.check_invoice_data(invoice_number_2, invoice_data_2)
        assert result == True, "Problem in invoice"

        # go to orders and check that only 1 product is in the order
        # go to orders
        orders = vendor.wait_for_el((By.LINK_TEXT, "Orders"))
        orders.click()
        view_button = vendor.wait_for_el((By.TAG_NAME, 'button'))
        view_button.click()
        # count number of rows
        rows = WebDriverWait(driver, vendor.DEFAULT_WAIT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#orderDetailRows>tr"))
        )
        assert len(rows) == 9, "In orders more that 1 elements"
    except Exception as exc:
        mes = str(exc)
        pytest.fail(msg=mes)
    finally:
        driver.quit()
