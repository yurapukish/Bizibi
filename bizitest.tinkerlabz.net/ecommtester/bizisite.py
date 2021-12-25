import logging
import time

from datetime import datetime
from .sitetest import Sitetester
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BizisiteBuyer(Sitetester):

    def create_account(self, base_username='Test_', password='PassWord'):
        logging.info("Attempt to create account")
        driver = self.get_driver()

        # find and click on the create account
        element = WebDriverWait(driver, self.DEFAULT_WAIT).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "top-right-link")))

        element.click()
        # driver.find_element(By.CLASS_NAME, "top-right-link").click()

        # assert that create account form is opened
        assert bool(driver.find_element(By.ID, "register")
                    ), "Create account form is not found"

        # fill the form
        # fill id form
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        username = base_username + str(timestamp)
        username = username[:20]
        test_email = "bizibitesting+" + str(timestamp) + "@gmail.com"

        user_data = {
            'username': username,
            'password': password,
            'email': test_email,
            'first_name': "TestFirstName",
            'last_name': "TestLastName",
            'phone': '1234567890',
        }

        # username max 20
        self.wait_for_el((By.ID, "username")).send_keys(user_data['username'])

        # fill passwords
        self.wait_for_el((By.ID, "password")).send_keys(user_data['password'])
        self.wait_for_el((By.ID, "password2")).send_keys(
            user_data['password'])

        # fill_email
        self.wait_for_el((By.ID, "Email")).send_keys(user_data['email'])

        # fill FirstName
        self.wait_for_el((By.ID, "FirstName")).send_keys(
            user_data['first_name'])

        # fill LastName
        self.wait_for_el((By.ID, "LastName")).send_keys(
            user_data['last_name'])
        self.wait_for_el((By.ID, "LastName")).send_keys(Keys.PAGE_DOWN)

        # Fill Address1
        self.wait_for_el((By.ID, "Address1")).send_keys("Address1")

        # Fill City
        self.wait_for_el((By.ID, "City")).send_keys("Test")
        element = self.wait_for_el((By.ID, "City"))
        driver.execute_script("arguments[0].scrollIntoView();", element)

        # Fill Phone
        self.wait_for_el((By.ID, "Phone")).send_keys(
            user_data['phone'] + Keys.TAB + Keys.RETURN)

        # fill location

        self.wait_for_el((
            By.CLASS_NAME, 'select2-search__field')).send_keys("Arena" + Keys.RETURN)

        # checkbox activate
        element = WebDriverWait(driver, self.DEFAULT_WAIT).until(
            EC.element_to_be_clickable((By.ID, 'agreeWithTermsCheckbox-indicator')))
        element.click()

        element = WebDriverWait(driver, self.DEFAULT_WAIT).until(
            EC.element_to_be_clickable((By.ID, 'formSubmitBtn')))
        element.click()

        # wait
        element = WebDriverWait(driver, self.DEFAULT_WAIT * 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success")))
        alert = element.text

        assert alert == "Your account has been successfully created, you may now proceed to log in"
        logging.info("Your account has been successfully created")

        return username, password, user_data, test_email



    def delete_all_items_from_card(self):
        logging.info("Try to delete all items from the card")
        driver = self.driver
        while len(driver.find_elements(By.CSS_SELECTOR, '.action>.item-remover')) > 0:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.action>.item-remover')))
            element.click()
            time.sleep(self.TIME)

        # assert that card is an empty
        assert driver.find_element(By.CSS_SELECTOR, '.section-header>.heading-design-h5').text \
               == 'YOUR CART IS EMPTY!'

        assert self.count_items_in_card() == 0, "Card icon is not empty"
        logging.info("Your card is empty now")

        return True

    def change_billing_address(self):
        logging.info("Change billing address")
        driver = self.driver

        # make a billing address

        time.sleep(self.TIME)
        ship_firstName = self.wait_for_el((By.ID, 'ship_firstName'))
        ship_firstName.send_keys("Good" + Keys.PAGE_DOWN)
        # fill last
        ship_lastName = self.wait_for_el((By.ID, 'ship_lastName'))
        ship_lastName.send_keys("Customer")

        # fill phone
        ship_phone = self.wait_for_el((By.ID, 'ship_phone'))
        ship_phone.send_keys("0987654321")

        # fill email
        ship_email = self.wait_for_el((By.ID, 'ship_email'))
        ship_email.send_keys('bizibitesting+customer@gmail.com')

        # fill location
        ship_city = self.wait_for_el((By.ID, "select2-ship_city-container"))
        ship_city.click()

        city2 = self.wait_for_el((By.CLASS_NAME, 'select2-search__field'))
        city2.send_keys("Arena" + Keys.RETURN)
        # adress ship_address
        ship_address = self.wait_for_el((By.ID, 'ship_address'))
        ship_address.send_keys('USA')

    def apply_coupon(self, coupon):
        logging.info("Try invalid coupon")
        # COUPONS
        time.sleep(self.TIME)
        driver = self.driver

        all_incart = driver.find_elements(By.CLASS_NAME, 'cart_description')

        driver.execute_script("arguments[0].scrollIntoView();", all_incart[-1])

        time.sleep(self.TIME)
        send_coupon = self.wait_for_el((By.CSS_SELECTOR, '[name="coupon"]'))
        send_coupon.send_keys(coupon)

        accept_coupon = self.wait_for_el((By.CSS_SELECTOR, 'form>div>button'))
        accept_coupon.click()

        # assert alert text
        time.sleep(self.TIME)
        alert_text = self.wait_for_el((By.CLASS_NAME, 'alert'))
        assert alert_text.text == "Invalid Coupon", "Problem with coupons"
