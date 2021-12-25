import sys
from datetime import *
from time import *
import time
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ecommtester.vendor import Vendor

from test.get_arguments import get_params

data = get_params()


def test_vendor_reg():
    global vendor
    try:
        browser, url, search_query, coupon, cookie = data['BROWSER_FIREFOX'], data['URL'], data['SEARCH'], data[
            'COUPON'], data['COOKIE']

        vendor = Vendor(browser, url, search_query, coupon, cookie)

        driver = vendor.get_driver()
        # set cookie
        vendor.set_cookie(cookie)

        # # prepare data for vendor acc
        username, test_email, company, description = vendor.vendors_data()
        result_create = vendor.create_vendor(username, test_email, company, description, excpected_result=True)
        print(username, test_email, company, description)

        assert result_create == True, "Account is not created"

        # Try to register the same store this should fail
        result_create2 = vendor.create_vendor(username, test_email, company, description, excpected_result=False)
        assert result_create2 == True, "Account is created with the same data"

        # find store
        vendor.find_store(company)
        STORE_URL = driver.current_url

        # assert created store data
        vendor.check_that_store_created_with_same_data(STORE_URL, description)

        # open home page


        vendor.recover_pass_vendor(username, test_email)

        # get first email
        vendor.open_Gmail_and_open_letter()
        time.sleep(vendor.TIME)
        link_in_email = vendor.wait_for_el((By.LINK_TEXT, 'clicking here'))
        link_in_email.click()
        #
        # # set new pass
        # # change password
        driver.switch_to.window(driver.window_handles[1])
        newpass = "Pa$$word!2"
        vendor.set_new_pass(newpass)

        # login with newpass
        try:
            login_new_pass = vendor.login_as_user(username, newpass)
            assert login_new_pass == True, "Password is not changed"
        except TimeoutException:
            time.sleep(vendor.TIME)
            login_new_pass = vendor.login_as_user(username, newpass)
            assert login_new_pass == True, "Password is not changed"

        # edit profile
        try:
            el = driver.find_elements(By.CSS_SELECTOR, '[dir="ltr"]')
            driver.execute_script("arguments[0].scrollIntoView();", el[-1])
            accept = vendor.wait_for_el((By.CLASS_NAME, 'acceptance-link'))
            accept.click()
        except Exception:
            edit = vendor.wait_for_el((By.CLASS_NAME, 'admin-bottom-link'))
            edit.click()

        edit = vendor.wait_for_el((By.CLASS_NAME, 'admin-bottom-link'))
        edit.click()

        # update profile
        update = "Update"
        vendor.update_vendor_profile(update)

        # open
        time.sleep(vendor.TIME)
        driver = vendor.get_driver()
        driver.get(STORE_URL)

        # ASSERTION THAT STORE DATA IS UPDATED
        store_name = vendor.wait_for_el((By.CSS_SELECTOR, '#about>div>div>div.section-header>h5'))
        store_name = store_name.text

        assert store_name.endswith(update.upper()) == True, "store name is not updated"

        store_description = vendor.wait_for_el((By.CSS_SELECTOR, '#about>div>div>div.row>div'))
        assert store_description.text.endswith(update) == True, "store name is not updated"
    except Exception as exc:

        mes = str(exc) + ' On the line: ' + str(sys.exc_info()[2].tb_lineno)
        pytest.fail(msg=mes, pytrace=True)
    finally:
        vendor.terminate_browser()
