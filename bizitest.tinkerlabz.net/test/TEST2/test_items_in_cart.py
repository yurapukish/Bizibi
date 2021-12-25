import logging
import sys
import time
import pytest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ecommtester.bizisite import BizisiteBuyer
from test.get_arguments import get_params


def test_manipulating_with_items():
    try:
        data = get_params()

        # open page
        browser, url, search_query = data['BROWSER_FIREFOX'], data['URL'], data['SEARCH']

        USER = BizisiteBuyer(browser, url, search_query)

        # Provide SEARCH_TERM
        USER.search_product(search_query)

        driver = USER.get_driver()

        # GET title -> first and second items title
        time.sleep(USER.TIME)
        all_items = driver.find_elements(
            By.CSS_SELECTOR, '.product-item-body > .card-title')
        name_first_item = all_items[0].text
        name_sec_item = all_items[1].text

        # add first item to card
        time.sleep(USER.TIME)
        all_products = driver.find_elements(
            By.CLASS_NAME, 'list-product-item-action')
        all_products[0].click()
        time.sleep(USER.TIME)

        # assert that 1 item on the card
        assert USER.count_items_in_card() == 1, "Wrong number of the items on the cart"

        # add 2 items to the card
        all_products[1].click()
        assert USER.count_items_in_card() == 2, "Wrong number of the items on the cart"

        # Assert that products title in the card
        open_card = USER.wait_for_el((By.CLASS_NAME, 'osahan-top-dropdown'))
        open_card.click()

        shop_items = driver.find_elements(By.TAG_NAME, 'strong')
        shop_titles = []
        for el in shop_items:
            shop_titles.append(el.text)
        if len(name_sec_item) > 45:
            name_sec_item = name_sec_item[:-5]

        assert name_first_item in shop_titles, 'Item is not found'
        assert name_sec_item in shop_titles, 'Item2 is not found'

        # view card
        view_card = USER.wait_for_el((By.LINK_TEXT, "VIEW CART"))
        view_card.click()

        time.sleep(USER.TIME)
        price = USER.wait_for_el((By.CSS_SELECTOR, 'tr>.price')).text

        # we should make price and total as numbers
        price = float(price[1:].replace(",", ""))

        # set quantity 10 also could change
        time.sleep(USER.TIME)
        quantity = USER.wait_for_el((By.CSS_SELECTOR, '[name*="quant"]'))
        quantity.send_keys(Keys.BACKSPACE + "10")

        # get quantity value
        quantity_value = quantity.get_attribute("value")

        time.sleep(USER.TIME)
        element = USER.wait_for_el((By.CLASS_NAME, 'widget'))
        element.click()

        time.sleep(USER.TIME)
        total_price = USER.wait_for_el((By.CSS_SELECTOR, '[id*="rowTotal_"]'))
        total_price = total_price.text

        total_price = float(total_price[1:].replace(",", ""))

        assert total_price == price * int(quantity_value)

        #  delete all from card
        delete_all_items = USER.delete_all_items_from_card()
        assert delete_all_items == True, "Cart is not empty"

        logging.info("TEST PASSED")
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        mes = str(exc) + ' On the line: ' + str(sys.exc_info()[2].tb_lineno)
        pytest.fail(msg=mes, pytrace=True)
    finally:
        USER.terminate_browser()


if __name__ == "__main__":
    test_manipulating_with_items()
