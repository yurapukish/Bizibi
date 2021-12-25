import pytest
import time
from ecommtester.bizisite import BizisiteBuyer
from test.get_arguments import get_params


def test_create_account(set_browser):
    '''
    Create an account and log into it
    '''
    driver, url, search, coupon = set_browser
    tester = BizisiteBuyer(driver, url, search, coupon)
    username, password, user_data = tester.create_account()
    time.sleep(3)
    print(username, password, user_data)
    result = tester.login_as_user(username, password, user_data)
    del tester
    assert result == True, "test_create_account failed"


def test_login():
    '''
    Login to a previously existing account. 

    If user_data is provided to tester.login_as_user the test will assert 
    the user_data matches what the user has in its real account
    '''
    data = get_params()

    tester = BizisiteBuyer(browser=data['BROWSER'], url=data['URL'])
    # username, password, email = test.create_account()
    username = 'bizibitesting'

    password = 'q1q1q1q1'

    user_data = {
        'username': username,
        'password': password,
        'email': "bizibitesting+qa@gmail.com",
        'first_name': "yura",
        'last_name': "Pukish",
        'phone': '+44500709231',
    }
    result = tester.login_as_user(username, password)
    del tester
    assert result == True, "test_login failed"
