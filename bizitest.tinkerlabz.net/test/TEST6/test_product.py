
import pytest
from selenium.webdriver.common.by import By
from ecommtester.bizisite import BizisiteBuyer
from test.get_arguments import get_params, get_filepath
from ecommtester.vendor import Vendor

data = get_params()


def test_product_activities():
    try:
        browser, url, vendor_username, vendor_password, search_query = data['BROWSER_FIREFOX'], data['URL'], \
                                                                       data['TEST_VENDOR_USERNAME'], data[
                                                                         'TEST_VENDOR_PASSWORD'], data['SEARCH']
        image1, image2, image3 = get_filepath(data['IMAGES']['IMAGE1']), get_filepath(data['IMAGES']['IMAGE2']), get_filepath(data['IMAGES']['IMAGE3'])
        vendor = Vendor(browser, url, vendor_username, vendor_password)
        driver = vendor.get_driver()
        login = vendor.login_as_user(vendor_username, vendor_password)
        print("login", login)
        assert login == True, "Login FAiled"

        # generate_data_for_creating_product
        products_data = vendor.generate_data_for_creating_product()

        category = vendor.add_product(products_data, image1, image2, image3)
        # search created product
        vendor.select_filter_and_search_product('name', products_data['name'])
        result = vendor.check_product_data_saved_correctly(products_data, category=category)
        assert result == True
        print("Result of saved data", result)
        # search
        for element in ['price', 'sku', 'legend', 'name']:
            if element != 'legend':
                vendor.select_filter_and_search_product(element, products_data[element])
            else:
                vendor.select_filter_and_search_product(element, products_data['quick_review'])

        modify_image = vendor.modify_image()
        assert modify_image == True
        print('Image modified success')
        vendor.terminate_browser()
        del vendor

        USER = BizisiteBuyer(browser, url)
        driver = USER.get_driver()

        # try to search product
        for search_query in ['sku', 'name', 'quick_review']:
            USER.search_product(products_data[search_query])
            count_items = driver.find_elements(By.CLASS_NAME, 'product-item')
            assert len(count_items) >0, 'Product is not found by user'

        USER.terminate_browser()
        del USER
        # go to edit product
        vendor = Vendor(browser, url, vendor_username, vendor_password)
        driver = vendor.get_driver()
        vendor.login_as_user(vendor_username, vendor_password)

        edit_product_data = vendor.generate_data_for_creating_product("EDIT_TEST")
        edited_category, result = vendor.edit_product(edit_product_data, active=True, wholesale=False)

        vendor.select_filter_and_search_product('name', edit_product_data['name'])
        result = vendor.check_product_data_saved_correctly(edit_product_data, category=edited_category)
        assert result == True
        print("Check that data is saved after editing", result)

        # price
        # USe higher “original price” then price” check the public site and make
        main_site = vendor.wait_for_el((By.LINK_TEXT, 'Main Site'))
        main_site.click()
        vendor.search_product(edit_product_data['name'])
        count_items = driver.find_elements(By.CLASS_NAME, 'product-item')
        if len(count_items) > 0:
            old_price = driver.find_elements(By.CLASS_NAME, 'product-desc-price')
            assert float(old_price[0].text.replace('$', "")) == edit_product_data['orig_price']

            price = driver.find_elements(By.CLASS_NAME, 'product-price')
            assert float(price[0].text.replace('$', "")) == edit_product_data['price']

            discount = driver.find_elements(By.CLASS_NAME, 'product-discount')
            assert 'SAVE $' in discount[0].text
            assert float(old_price[0].text.replace('$', "")) - float(price[0].text.replace('$', "")) == float(discount[0].text.replace('SAVE $',''))
            print("Course discount right")
        else:
            pytest.fail('Product is not found')

        # Leave original price blank (optional)
        driver.find_element(By.LINK_TEXT, "My Admin Panel").click()
        edit_product_data["orig_price"] = ' '
        print(edit_product_data)
        edited_category, result = vendor.edit_product(edit_product_data, active=True, wholesale=False)
        assert result == True, "An error occurred while Leave original price blank "
        print("Leave original price blank", result)

        # USe higher “original price” then price” check the public site and make
        edit_product_data["orig_price"] = str(edit_product_data["price"]/2)
        print(edit_product_data["orig_price"], edit_product_data["price"])
        result_price = vendor.edit_product(edit_product_data, active=True, wholesale=False)
        assert result_price == True

        # Activate/Deactivate product
        deactivate = vendor.edit_product(active=False)
        assert deactivate == True, 'Deactivation is failed'
        vendor.select_filter_and_search_product('name', edit_product_data['name'])
        result = vendor.check_product_data_saved_correctly(edit_product_data, category=edited_category)
        assert result == True
        print("Check that vendor see deactivated product", result)
        vendor.logout()
        vendor.search_product(edit_product_data['name'])
        count_items = driver.find_elements(By.CLASS_NAME, 'product-item')
        assert len(count_items) == 0, "Product is not deactivated"
        print("Product deactivated ok")


        # Wholesale only
        # Activate/Deactivate product
        vendor.login_as_user(vendor_username, vendor_password)
        wholesale = vendor.edit_product(active=True, wholesale=True)
        assert wholesale == True, 'Make product wholesale only is failed'
        vendor.select_filter_and_search_product('name', edit_product_data['name'])
        result = vendor.check_product_data_saved_correctly(edit_product_data, category=edited_category)
        assert result == True
        print("Check that vendor see wholesale product", result)
        vendor.logout()
        vendor.search_product(edit_product_data['name'])
        count_items = driver.find_elements(By.CLASS_NAME, 'card-title')
        assert len(count_items) > 0, "wholesale product is  not found"
        count_items[0].click()

        # find price
        price_text = vendor.wait_for_el((By.ID, 'finalPrice')).text.strip()
        assert price_text == 'Not available for retail'
        print(price_text)
    finally:
        driver.quit()
