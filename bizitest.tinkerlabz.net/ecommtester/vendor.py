import logging
import random
import string
import os
import hashlib
import time
from datetime import datetime
from telnetlib import EC

from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from test.get_arguments import get_filepath, get_params
from .sitetest import Sitetester
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

data = get_params()


class Vendor(Sitetester):

    def vendors_data(self):
        logging.info("Prepare data for vendor")

        # data for vendor
        time.sleep(self.TIME)

        now = datetime.now()
        timestamp = datetime.timestamp(now)
        username = "Test" + str(timestamp)
        username = username[:20].replace('.', '')
        test_email = "bizibitesting+" + str(timestamp) + "@gmail.com"
        # random company name
        company = 'E2E' + ''.join(random.choices(string.ascii_lowercase, k=12))
        description = "description" + company
        return username, test_email, company, description

    def create_vendor(self, username, test_email, company, description, excpected_result):

        logging.info("Attempt to create vendor account")

        driver = self.get_driver()

        #  Click "Stores" (in the top bar)
        store_button = self.wait_for_el((By.LINK_TEXT, 'STORES'))
        store_button.click()

        #  Find "Join our team!" and click it
        join_button = self.wait_for_el((By.CLASS_NAME, 'card-title'))
        if join_button.text == "Join our team!":
            join_button.click()
        else:
            pytest.fail("Join our team! -> is not found")
        time.sleep(self.TIME)

        #  Select any of the available packages, if no packages fail test and stop
        select_pack = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.LINK_TEXT, 'SELECT')))

        if len(select_pack) > 0:
            select_pack[0].click()
        else:
            pytest.fail("No packages")
        # Fill in the form and submit it

        css_selector_id = ["username", "password", "company", "first_name", "last_name", "email", "phone", "website",
                           "address", "description"]
        input_value = [username, "Pa$$word", company, "My first_name", "My last_name", test_email, "phone",
                       "website", "address", description]
        for ele in range(10):
            element = self.wait_for_el((By.ID, css_selector_id[ele]))
            element.send_keys(input_value[ele])
            if ele == 8:
                driver.execute_script(
                    "arguments[0].scrollIntoView();", element)
                # fill location
                time.sleep(self.TIME)
                element.send_keys(Keys.TAB + Keys.RETURN)
                driver.find_element(
                    By.CLASS_NAME, 'select2-search__field').send_keys("Arena" + Keys.RETURN)
                time.sleep(self.TIME)
        driver.find_element(By.ID, 'code').send_keys('12345')
        # checkbox activate
        element = self.wait_for_el(
            (By.CSS_SELECTOR, '.form-group:nth-child(18)>.custom-control'))
        element.click()

        element = self.wait_for_el((By.CSS_SELECTOR, '[data-action="submit"]'))
        element.click()

        if excpected_result:
            alert = self.wait_for_el((By.CLASS_NAME, "text-success"))
            # assert alert
            alert = alert.text
            time.sleep(self.TIME)
            assert alert == "Your account has been successfully created" or \
                   alert == "Please check your email to activate your account"
            logging.info("Your account has been successfully created")
            return True
        elif not excpected_result:
            error_message = self.wait_for_el(
                (By.ID, "validate_username_message"))
            error_message = error_message.text

            if error_message.endswith('is not available'):
                return True
            else:
                logging.info("Error message is not found")
                return False

    def set_cookie(self, cookie):
        logging.info("Attempt to create vendor cookie")
        driver = self.get_driver()

        data = datetime.today().strftime('%Y-%m-%d')
        data_cookie = cookie + "." + data
        create_cookie = hashlib.sha1(data_cookie.encode('utf-8'))
        create_cookie = create_cookie.hexdigest()
        cookies = {'name': 'E2ETEST', 'value': create_cookie}
        driver.add_cookie(cookies)

        return True

    def find_store(self, company):
        logging.info("Try find the store")
        driver = self.driver

        # Click "Stores" (in the top bar)
        store_button = self.wait_for_el((By.LINK_TEXT, 'STORES'))
        store_button.click()

        # find all pages
        all_pages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "page-item")))
        driver.execute_script("arguments[0].scrollIntoView();", all_pages[1])
        count_pages = len(all_pages) - 2
        all_pages[1].click()
        current_page = driver.current_url
        current_page = current_page[:-1]
        print(current_page)
        for pages in range(1, int(count_pages) + 1):
            print(f"{current_page}{pages}")
            driver.get(f"{current_page}{pages}")
            # try to find
            all_mag = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "card-title")))
            all_text = [i.text for i in all_mag]

            if company in all_text:
                logging.info("Vendor shop is found")
                # click on the name

                logging.info("Company name is : ", {company})
                comp_ind = all_text.index(company)

                open = driver.find_elements(By.CLASS_NAME, 'card-body')
                open[int(comp_ind)].click()
                time.sleep(self.TIME)
                break
        else:
            pytest.fail("VENDOR IS NOT FOUND")

    def check_that_store_created_with_same_data(self, url, description):
        logging.info("Assert store descruiption and other data")
        driver = self.driver
        driver.get(url)

        # click on the about the store
        about_store = self.wait_for_el((By.ID, 'about-tab'))
        about_store.click()
        about_store_description = self.wait_for_el(
            (By.CSS_SELECTOR, '#about>div>div>div.row>div'))
        about_store_description = about_store_description.text
        assert about_store_description == description, "About store description is not same"

        # VISIT STORE visit-tab
        click_here_to_visit_store = self.wait_for_el((By.ID, 'visit-tab'))
        click_here_to_visit_store.click()
        assert driver.current_url != url, "Store is not opened"
        return True

    def recover_pass_vendor(self, username, test_email):
        logging.debug("Change password")

        driver = self.driver

        element = self.wait_for_el((By.LINK_TEXT, 'Sign In'))
        element.click()

        # after clicking new sing up window is opened so we should jump to it
        driver.switch_to.active_element
        # click on the forgot poss
        element = self.wait_for_el((By.LINK_TEXT, 'Forgot your password?'))
        element.click()
        time.sleep(self.TIME)
        checkbox = self.wait_for_el(
            (By.CSS_SELECTOR, ".custom-control:nth-child(1)"))
        checkbox.click()

        user_name_id = self.wait_for_el((By.ID, 'user_name'))
        user_name_id.send_keys(username)
        time.sleep(self.TIME)
        email_id = self.wait_for_el((By.ID, 'user_email'))
        email_id.send_keys(test_email + Keys.RETURN)
        time.sleep(self.TIME)
        alert = self.wait_for_el((By.CLASS_NAME, 'alert-success'))
        assert alert.text == 'Please check your email for instructions on how to reset your password', "Recovery pass is failed"

    def update_vendor_profile(self, update):
        logging.info('Update profile')

        driver = self.driver

        # edit profile
        css_selectors = ['company', 'first_name', 'last_name', 'address', 'city', 'zip', 'latitude', 'longitude',
                         'description']
        for id in css_selectors:
            el = self.wait_for_el((By.ID, id))
            el.send_keys(update)

        save = self.wait_for_el((By.CSS_SELECTOR, '[value="Save"]'))
        save.click()

    def invoice_form(self, file_path):

        logging.info('Create invoice')

        driver = self.driver
        file_path = r'{}'.format(file_path)
        # file_path = r'C:\Users\Admin\PycharmProjects\bizitest.tinkerlabz.net\test\TEST5\YuraTestCase.pdf'
        # open invoice
        invoice_link = driver.find_element(By.LINK_TEXT, 'INVOICE2EMAIL')
        invoice_link.click()
        general_css_selectors = ['recipientName', 'recipientEmail', 'recipientPhone', 'invoiceFile', 'descriptionFld',
                                 'totalToCollect', 'validityPeriod']
        user_load_data = ['Yura', "bizibitesting@gmail.com", '123456789', file_path,
                          "This field is used in the email sent to the receipient", '777', '']
        for element in range(len(general_css_selectors)):
            field = self.wait_for_el((By.ID, general_css_selectors[element]))
            field.send_keys(user_load_data[element])

        send = self.wait_for_el((By.CLASS_NAME, 'submitBtn'))
        send.click()

        # assert
        alert_message = self.wait_for_el((By.ID, 'feedback'))
        assert 'Invoice was sent correctly. The Order Number for this invoice is' in alert_message.text, 'Invoice is not created'

        invoice_number = alert_message.text[-3:]

        return invoice_number, user_load_data

    def check_invoice_data(self, invoice_number, invoice_data):

        logging.info('Create invoice')
        driver = self.driver
        # # open home page and click on the orders
        home = self.wait_for_el((By.LINK_TEXT, "Home"))
        home.click()
        order = self.wait_for_el((By.CLASS_NAME, 'home-warning-text'))
        order.click()

        #  assert Order_number == invoice_number
        order_number = self.wait_for_el(
            (By.CSS_SELECTOR, 'tr:nth-child(1)>td:nth-child(1)'))
        assert order_number.text == invoice_number, "Order_number != invoice_number"

        # status  not Payment Pending
        status = self.wait_for_el((By.CSS_SELECTOR, 'td:nth-child(7)'))
        assert status.text == "Payment Pending", "Order status is not Payment Pending"

        # assert amount

        amount = invoice_data[-2]
        amount_in_order = self.wait_for_el((By.CLASS_NAME, 'money-text'))
        amount_in_order = amount_in_order.text[1:]

        assert float(amount) == float(
            amount_in_order), "Wrong order Total Amount"
        return True

    def add_product(self, products_data, image1, image2, image3):

        logging.info('Add product')
        driver = self.driver
        # find link Products
        product_link = self.wait_for_el((By.LINK_TEXT, 'Products'))
        product_link.click()

        # find add product
        add_product_link = self.wait_for_el((By.LINK_TEXT, 'Add New Product'))
        add_product_link.click()

        # add category
        category = []
        for i in range(4):

            cat = driver.find_elements(By.ID, f'category_1_{i}')
            print("Category ", len(cat), f'On step {i + 1}')
            if len(cat) > 0:
                select_object = Select(self.wait_for_el((By.ID, f'category_1_{i}')))
                all_available_options = select_object.options
                value = random.randint(1, len(all_available_options) - 1)
                select_object.select_by_index(value)
                category.append(all_available_options[value].text)
            else:
                break
        print(category)
        # fill name
        name = self.wait_for_el((By.ID, 'name'))
        name.send_keys(products_data["name"])

        # fill sku
        sku = self.wait_for_el((By.ID, 'sku'))
        sku.send_keys(products_data["sku"])

        # quick_review
        quick_review = self.wait_for_el((By.CSS_SELECTOR, '#quill_legend .ql-editor'))
        quick_review.click()
        quick_review.send_keys(products_data["quick_review"])

        # description
        description = self.wait_for_el((By.CSS_SELECTOR, '#quill_description .ql-editor'))
        description.send_keys(products_data["description"])

        # add image1, image2, image3

        add_img = driver.find_element(By.CSS_SELECTOR, '[type="file"]')
        print("try to add image")
        add_img.send_keys(image1)
        time.sleep(1)
        add_img.send_keys(image2)
        time.sleep(1)
        add_img.send_keys(image3)

        # price
        orig_price = self.wait_for_el((By.ID, 'old_price'))
        orig_price.send_keys(products_data["orig_price"])
        sale_price = self.wait_for_el((By.ID, 'price'))
        sale_price.send_keys(products_data["price"])

        # submit button
        create_product = self.wait_for_el((By.ID, 'submit-button'))
        create_product.click()

        # assert
        alert_text = self.wait_for_el((By.CSS_SELECTOR, ".alert .underline-link"))
        alert_text = alert_text.text.strip()
        assert alert_text == "The new product has been added successfully", "Product is not created"
        print("product created")
        return category

    def generate_data_for_creating_product(self, edit="Test_"):
        logging.info('Generate data for crating product')
        driver = self.driver
        sku = edit + str(random.randint(1, 999999))
        name = edit + str(random.randint(1, 999999))
        orig_price = random.randint(3, 100)

        price = random.randint(1, orig_price)
        quick_review = edit + "Smart Cat Toys Interactive Ball Cat"
        description = edit + "Smart Cat Toys Interactive Ball Catnip Cat Training Toy Pet Playing Ball Pet Squeaky Supplies Products Toy for Cats Kitten Kitty"

        data_for_product = {"sku": sku,
                            "name": name,
                            "orig_price": orig_price,
                            "price": price,
                            "quick_review": quick_review,
                            "description": description
                            }
        print(data_for_product)
        return data_for_product

    def check_product_data_saved_correctly(self, data, category):
        logging.info('Check products data')
        driver = self.driver
        product_on_site = driver.find_elements(By.CSS_SELECTOR, 'tr>td')
        product_on_site_category = product_on_site[4].text.split(' > ')
        for element in product_on_site_category:
            assert element in category
        # assert sku
        product_on_site_sku = product_on_site[6].text
        assert product_on_site_sku == data['sku'], 'SKU is not match'

        # assert price
        product_on_site_price = product_on_site[5].text
        assert float(product_on_site_price.replace("$", '')) == data[
            'price'], f'Price is not match. product_on_site_price {product_on_site_price}, {data["price"]}'

        # assert name
        product_on_site_name = product_on_site[7].text
        assert product_on_site_name == data['name'], 'Name is not match'

        # assert legend
        product_on_site_legend = self.wait_for_el((By.CSS_SELECTOR, 'tr>td>p'))
        product_on_site_legend = product_on_site_legend.text
        assert product_on_site_legend in data['quick_review'], "Review is not match"

        return True

    def select_filter_and_search_product(self, filter_param, search_title):
        logging.info('Filter params: price, sku, name, legend, visits')
        driver = self.driver
        # find link Products
        product_link = self.wait_for_el((By.LINK_TEXT, 'Products'))
        product_link.click()

        select_object = Select(self.wait_for_el((By.CSS_SELECTOR, '[name="comboSearch"]')))

        select_object.select_by_value(filter_param)

        search_input = self.wait_for_el((By.CSS_SELECTOR, '[name="textSearch"]'))
        search_input.send_keys(search_title)

        # click search button
        search_button = self.wait_for_el((By.CSS_SELECTOR, '[value = " Search "]'))
        search_button.click()
        time.sleep(1)

        # assert that product is found
        item = driver.find_elements(By.CLASS_NAME, 'yellow-back-text')
        assert len(item) > 0, "Product is not found"
        print("product filtered and found")

    def edit_product(self, data=None, active=None, wholesale=None):
        logging.info('Edit product')
        driver = self.driver
        # find link Products
        product_link = self.wait_for_el((By.LINK_TEXT, 'Products'))
        product_link.click()

        # find edit product button
        edit_product_link = self.wait_for_el((By.CSS_SELECTOR, 'tbody>tr>td>a'))
        edit_product_link.click()
        if data:
            # add category
            category = []
            for i in range(4):

                cat = driver.find_elements(By.ID, f'category_1_{i}')
                print("Category ", len(cat), f'On step {i + 1}')
                if len(cat) > 0:
                    select_object = Select(self.wait_for_el((By.ID, f'category_1_{i}')))
                    all_available_options = select_object.options
                    value = random.randint(1, len(all_available_options) - 1)
                    select_object.select_by_index(value)
                    category.append(all_available_options[value].text)
                else:
                    break
            print(category)
            # fill name
            name = self.wait_for_el((By.ID, 'name'))
            name.clear()
            name.send_keys(data["name"])

            # fill sku
            sku = self.wait_for_el((By.ID, 'sku'))
            sku.clear()
            sku.send_keys(data["sku"])

            # quick_review
            quick_review = self.wait_for_el((By.CSS_SELECTOR, '#quill_legend .ql-editor'))
            quick_review.click()
            quick_review.clear()
            quick_review.send_keys(data["quick_review"])

            # description
            description = self.wait_for_el((By.CSS_SELECTOR, '#quill_description .ql-editor'))
            description.clear()
            description.send_keys(data["description"])

            # price
            orig_price = self.wait_for_el((By.ID, 'old_price'))
            orig_price.clear()
            orig_price.send_keys(data["orig_price"])
            sale_price = self.wait_for_el((By.ID, 'price'))
            sale_price.clear()
            sale_price.send_keys(data["price"])
            if data["orig_price"] != ' ' and float(data["orig_price"]) < float(data["price"]):
                element = self.wait_for_el((By.CLASS_NAME, 'danger'))
                assert element.is_displayed(), "Price error is not displayed"
                return True

        # select active
        select_object = Select(self.wait_for_el((By.NAME, 'active')))

        if not active:
            value = 1
        # 1-yes  0-No
        else:
            value = 0
        select_object.select_by_index(value)

        # wholesales
        select_object = Select(self.wait_for_el((By.NAME, 'b2bonly')))
        # 1-yes  0-No
        if not wholesale:
            value = 1
        else:
            value = 0
        select_object.select_by_index(value)

        # submit button
        create_product = self.wait_for_el((By.CSS_SELECTOR, '[value="Save"]'))
        create_product.click()

        # assert
        alert_text = self.wait_for_el((By.CLASS_NAME, "medium-font"))
        alert_text = alert_text.text.strip()
        assert alert_text == "The new values have been saved successfully!", "Product is not edited"
        print("product created")
        if data:
            return category, True
        else:
            return True

    def modify_image(self):
        logging.info('Modify image')
        driver = self.driver
        # find link Products
        product_link = self.wait_for_el((By.LINK_TEXT, 'Products'))
        product_link.click()

        # find edit product button
        edit_product_link = self.wait_for_el((By.LINK_TEXT, 'Modify'))
        edit_product_link.click()

        # try to delete image
        delete_list = driver.find_elements(By.CSS_SELECTOR, '[alt="Delete"]')
        delete_list[-1].click()

        # try to Restore BG
        restore_bg = driver.find_elements(By.CSS_SELECTOR, '[alt="Restore BG"]')
        if len(restore_bg) > 0:
            restore_bg[-1].click()

        # try to grad and drop
        action = ActionChains(driver)
        all_image = driver.find_elements(By.CSS_SELECTOR, '[ondragstart="javascript:img_drag_start(this)"]')
        source1 = all_image[1]
        target1 = all_image[0]
        action.drag_and_drop(source1, target1).perform()

        add_img = driver.find_element(By.ID, 'images')
        print("try to add image")

        image1 = get_filepath(data['IMAGES']['IMAGE3'])
        print(image1)
        add_img.send_keys(image1)
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, '[value=" Submit "]').click()

        # choose random template
        all_templates = driver.find_elements(By.CLASS_NAME, 'flyer-thumbnail')
        all_templates[random.randint(0, len(all_templates) - 1)].click()

        return True

    def add_user_to_store(self, username, user_email):
        logging.info('add_user_to_store')
        driver = self.driver

        # go to mange user
        manage_user = self.wait_for_el((By.LINK_TEXT, 'Settings'))
        manage_user.click()

        # check if email available
        email_field = self.wait_for_el((By.ID, 'userEmail'))
        email_field.send_keys(user_email)

        check_but = self.wait_for_el((By.ID, 'checkEmail'))
        check_but.click()

        # check result
        check_result = self.wait_for_el((By.ID, 'emailResult'))
        check_result = check_result.text

        # here is typo mistake
        assert check_result == f'{user_email} avaialble'

        if check_result.endswith('avaialble'):
            username_f = self.wait_for_el((By.ID, 'username'))
            username_f.send_keys(username)

            firstName = self.wait_for_el((By.ID, 'firstName'))
            firstName.send_keys('User_' + ''.join(random.choices(string.ascii_lowercase, k=12)))

            lastName = self.wait_for_el((By.ID, 'lastName'))
            lastName.send_keys('User_' + ''.join(random.choices(string.ascii_lowercase, k=12)))

            phone = self.wait_for_el((By.ID, 'phone'))
            phone.send_keys('1234567890')

            create_user = self.wait_for_el((By.CSS_SELECTOR, '[name="addUser"]'))
            create_user.click()

            # get password
            create_message = driver.find_element(By.ID, 'feedback')
            assert create_message.is_displayed()
            password = create_message.text.replace(f'User {username} successfully created with password ', '')
            password = password.strip()

            return password

    def assert_two_roles(self, expect=True):
        logging.info('Modify image')
        driver = self.driver

        if expect:
            # find link My profile
            my_profile = self.wait_for_el((By.ID, 'VendorProfileLinker'))
            my_profile.click()

            all_links = self.driver.find_elements(By.CLASS_NAME, 'dropdown-item')
            assert all_links[0].text == "My Profile"
            assert all_links[1].text == "Vendor Admin Panel"
            return True
        else:
            assert len(self.driver.find_elements(By.ID, 'VendorProfileLinker')) == 0, "Should be only 1 link 'My Profile"
            return True

    def delete_user(self):
        logging.info('delete_user_from_store')
        driver = self.driver

        # go to mange user
        manage_user = self.wait_for_el((By.LINK_TEXT, 'Settings'))
        manage_user.click()

        while True:
            all_users = driver.find_elements(By.CSS_SELECTOR, 'td>button')
            count = len(driver.find_elements(By.CSS_SELECTOR, 'td>button'))
            if count == 0:
                break
            else:
                print("now users:", count)
                all_users[-1].click()
                delete = self.wait_for_el((By.CSS_SELECTOR, '[name="removeEmail"]'))
                delete.click()

                # alert
                alert = self.wait_for_el((By.ID, 'feedback')).text
                text = 'User successfully removed from organization'

                assert text == alert, "user is not deleted"



