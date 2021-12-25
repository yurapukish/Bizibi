import logging
import time

import pytest
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from test.get_arguments import get_params
from ecommtester.bizisite import BizisiteBuyer

data = get_params()


def test_creating_acc_full_flow():

    try:
        # create acc
        browser, url = data['BROWSER'], data['URL']
        USER = BizisiteBuyer(browser, url)
        acc_created = USER.create_account()

        username, password, user_data, test_email = acc_created

        # login
        try:
            login_result = USER.login_as_user(username, password, user_data)
            assert login_result == True, "test_create_account failed"
        except TimeoutException:
            time.sleep(USER.TIME)
            login_result = USER.login_as_user(username, password, user_data)
            assert login_result == True, "test_create_account failed"
        USER.logout()

        # forgot pass
        driver = USER.get_driver()

        # Sign back in but use “Forgot password”
        element = USER.wait_for_el((By.LINK_TEXT, 'Sign In'))
        element.click()

        # after clicking new sing up window is opened so we should jump to it
        driver.switch_to.active_element
        # click on the forgot poss
        element = USER.wait_for_el((By.LINK_TEXT, 'Forgot your password?'))
        element.click()

        # fill the email and asset alert text
        time.sleep(USER.TIME)
        email = USER.wait_for_el((By.ID, 'user_email'))
        email.send_keys(test_email + Keys.RETURN)

        forgot_pass_alert = USER.wait_for_el((By.CLASS_NAME, 'alert-success'))
        assert forgot_pass_alert.text == \
               'Please check your email for instructions on how to reset your password'

        # get first email
        USER.open_Gmail_and_open_letter()
        time.sleep(USER.TIME)
        # did not receive an email
        link_in_email = USER.wait_for_el((By.LINK_TEXT, 'clicking here'))
        link_in_email.click()

        # change password
        driver.switch_to.window(driver.window_handles[1])
        newpass = data['NEWPASS']
        USER.set_new_pass(newpass)

        # login with newpass
        try:
            login_new_pass = USER.login_as_user(username, newpass)
            assert login_new_pass == True, "Password is not changed"
        except TimeoutException:
            time.sleep(USER.TIME + 5)
            login_new_pass = USER.login_as_user(username, newpass)
            assert login_new_pass == True, "Password is not changed"
    except Exception as e:
        pytest.fail(str(e))
    finally:
        USER.terminate_browser()
