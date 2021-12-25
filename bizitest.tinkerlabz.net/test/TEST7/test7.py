from datetime import *
from time import *
import time

from test.get_arguments import get_params, get_filepath
from ecommtester.vendor import Vendor

data = get_params()


def test_extra_users():
    try:
        browser, url, vendor_username, vendor_password = data['BROWSER_FIREFOX'], data['URL'], \
                                                         data['TEST_VENDOR_USERNAME'], data['TEST_VENDOR_PASSWORD'],

        vendor = Vendor(browser, url, vendor_username, vendor_password)
        driver = vendor.get_driver()
        login = vendor.login_as_user(vendor_username, vendor_password)
        print("login", login)
        assert login == True, "Login FAiled"

        # add new user
        print("prepare data for new user")
        username, user_email = vendor.vendors_data()[0], vendor.vendors_data()[1]
        print(username, user_email)
        # bizibitesting+1632645462.230891@gmail.com
        user_password = vendor.add_user_to_store(username, user_email)
        print(user_password)
        vendor.logout()

        # assert that new user has two roles
        print('User')
        vendor.login_as_user(username, user_password)
        roles_result = vendor.assert_two_roles()
        assert roles_result == True, "user doesn't have two roles"

        vendor.logout()

        # delete user in the store
        vendor.login_as_user(vendor_username, vendor_password)
        vendor.delete_user()
        vendor.logout()
        # login as a user
        vendor.login_as_user(username, user_password)
        roles_result = vendor.assert_two_roles(expect=False)
        assert roles_result == True, "Roles result failed"

    finally:
        vendor.terminate_browser()
