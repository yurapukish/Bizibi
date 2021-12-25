import logging
import sys
import time
import re
import random
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from ecommtester.bizisite import BizisiteBuyer
from test.get_arguments import get_params

data = get_params()


def test_order_flow():
    browser, url, search_query, coupon = data['BROWSER'], data['URL'], data['SEARCH'], data['COUPON']
    USER = BizisiteBuyer(browser, url, search_query, coupon)

    # Search for items (should be use a defined SKU for product and pass it as a parameter)
    # Provide SEARCH_TERM
    USER.search_product(search_query)

    driver = USER.get_driver()

    # find all items
    time.sleep(USER.TIME)
    all_items = driver.find_elements(
        By.CSS_SELECTOR, '.product-item-body>.card-title')
    if len(all_items) > 4:
        # add first 3 to card
        all_card_icon = driver.find_elements(
            By.CLASS_NAME, 'list-product-item-action')
        for i in range(3):
            time.sleep(USER.TIME)
            all_card_icon[i].click()

        # view detail about 4 product
        # time.sleep(USER.TIME)
        all_items[3].click()

        # now on the card should be 3 items

        assert USER.count_items_in_card() == 3, "Wrong amount of items on the cart"

        # add 1 more quantity
        time.sleep(USER.TIME)
        element = USER.wait_for_el((By.CSS_SELECTOR, '[data-type="plus"]'))
        element.click()

        time.sleep(USER.TIME)
        element = USER.wait_for_el((By.CSS_SELECTOR, 'form > button'))
        element.click()

        # 3 + 2 = 5 items on the card
        time.sleep(USER.TIME)
        assert USER.count_items_in_card() == 5, "Wrong amount of items on the cart"

        driver.back()

        # view detail about 5 product
        time.sleep(USER.TIME)
        all_items = driver.find_elements(
            By.CSS_SELECTOR, '.product-item-body > .card-title')
        all_items[4].click()

        # add 1 more quantity
        time.sleep(USER.TIME)
        increase_quantity = USER.wait_for_el(
            (By.CSS_SELECTOR, '[data-type="plus"]'))
        increase_quantity.click()

        time.sleep(USER.TIME)
        item_4 = USER.wait_for_el((By.CSS_SELECTOR, 'form > button'))
        item_4.click()

        # 5 + 2 = 7 items on the card
        time.sleep(USER.TIME)
        assert USER.count_items_in_card() == 7, "Wrong amount of items on the cart"
    elif 2 <= len(all_items) <= 4:
        count = 0
        # add first 1 to card
        all_card_icon = driver.find_elements(
            By.CLASS_NAME, 'list-product-item-action')
        for i in range(len(all_card_icon) - 1):
            all_card_icon[i].click()
            time.sleep(USER.TIME)
            count += 1

        # assert amount of items
        time.sleep(USER.TIME)
        assert USER.count_items_in_card() == count, "Wrong amount of items on the cart"

        # add 1 more quantity for item
        time.sleep(USER.TIME)
        # view detail about 4 product
        all_items[-1].click()

        increase_quantity = USER.wait_for_el(
            (By.CSS_SELECTOR, '[data-type="plus"]'))
        increase_quantity.click()

        time.sleep(USER.TIME)
        card = USER.wait_for_el((By.CSS_SELECTOR, 'form > button'))
        card.click()

        # count + 2 items on the card
        time.sleep(USER.TIME)
        assert USER.count_items_in_card() == count + \
            2, "Wrong number of the items on the card"
        driver.back()
    elif len(all_items) < 2:
        logging.info(
            "Enter another search query. Amount of items to low. TEST Failed")

    # click on the cart
    card = USER.wait_for_el((By.CLASS_NAME, 'osahan-top-dropdown'))
    card.click()

    # open view cart
    element = USER.wait_for_el((By.LINK_TEXT, "VIEW CART"))
    element.click()

    # find element with quantity 1
    all_items = driver.find_elements(By.CSS_SELECTOR, '[name*="quant"]')
    all_quantity_minus = driver.find_elements(
        By.CSS_SELECTOR, '.qty [data-type="minus"]')
    all_quantity_plus = driver.find_elements(
        By.CSS_SELECTOR, '.qty [data-type="plus"]')
    # update quantity
    for items in range(len(all_items)):
        time.sleep(USER.TIME)
        if all_items[items].get_attribute("value") == "1":
            driver.execute_script(
                "arguments[0].scrollIntoView();", all_quantity_plus[items])
            all_quantity_plus[items].click()
        elif all_items[items].get_attribute("value") == "2":
            driver.execute_script(
                "arguments[0].scrollIntoView();", all_quantity_minus[items])
            all_quantity_minus[items].click()

    # close cookie
    close_cookie = USER.wait_for_el((By.CLASS_NAME, 'cookieinfo-close'))
    close_cookie.click()

    # checkout
    time.sleep(USER.TIME)
    target = all_items[len(all_items) - 1]
    target.send_keys(Keys.PAGE_DOWN)

    element = USER.wait_for_el((By.CSS_SELECTOR, '.form-next-btn'))
    element.click()

    # find and fill username and pass
    time.sleep(USER.TIME)
    USERNAME = data['USERNAME']
    PASSWORD = data['PASSWORD']
    login_result = USER.login_as_user(USERNAME, PASSWORD)
    assert login_result == True
    # click on the billing checkbox or  make a billing address
    if random.randint(0, 1) == 1:
        # click on the billing checkbox
        el = driver.find_element(By.ID, 'delivery')
        driver.execute_script("arguments[0].scrollIntoView();", el)
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'custom-control-description')))
        element.click()
    else:
        USER.change_billing_address()

    element = USER.wait_for_el((By.ID, 'submit_btn'))
    element.click()

    # if coupon try to use it
    if coupon:
        USER.apply_coupon(coupon)

    # next
    element = USER.wait_for_el(
        (By.CSS_SELECTOR, '[data-callback="proceedToPayment"]'))
    element.click()

    element = USER.wait_for_el((By.CSS_SELECTOR, '#submit_btn'))
    element.click()

    # checkout
    USER.checkout()

    # check an email confirmation
    time.sleep(USER.TIME + 2)
    USER.open_Gmail_and_open_letter()

    # assertion  Receipt #227 for your order from bizitest
    text_from_letter = driver.find_element(By.CSS_SELECTOR, '.ha>h2').text

    pattern = r'Receipt #\d\d\d for your order from '

    result = re.match(pattern, text_from_letter)

    assert bool(result) == True, "text from the letter is not the same"
    logging.info("TEST Passed")


if __name__ == "__main__":
    test_order_flow()
