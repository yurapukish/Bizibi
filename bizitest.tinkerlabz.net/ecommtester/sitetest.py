import logging
from re import T
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from urllib.parse import urlparse, parse_qs


class Sitetester():
    driver = None

    TIME = 1
    DEFAULT_WAIT = 10
    LONG_WAIT = 20

    def __init__(self, browser=None, url=None, search=None, coupon=None, cookie=None):

        self.url = url
        self.search = search
        self.coupon = coupon
        self.cookie = cookie
        self.init_browser(browser)

    def __del__(self):
        self.terminate_browser()

    def init_browser(self, browser):
        logging.debug("Init browser")
        # set browser
        if browser == "Chrome":
            options = webdriver.ChromeOptions()
            options.add_argument('ignore-certificate-errors')

            driver = webdriver.Chrome(
                ChromeDriverManager().install(), options=options)
        else:
            profile = webdriver.FirefoxProfile()
            profile.accept_untrusted_certs = True
            driver = webdriver.Firefox(
                executable_path=GeckoDriverManager().install(), firefox_profile=profile)

        # open a home_page_link

        driver.maximize_window()
        logging.info("URL", self.url)
        driver.get(self.url)
        driver.implicitly_wait(self.LONG_WAIT)
        self.driver = driver

    def terminate_browser(self):
        logging.debug("Terminating browser")
        self.get_driver().quit()

    def get_driver(self):
        return self.driver

    def open_Gmail_and_open_letter(self, email='bizibitesting@gmail.com', password='b1z1t3st1ng'):
        logging.debug("Open email letter")
        driver = self.get_driver()
        driver.get(
            "https://accounts.google.com/signin/v2/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F"
            "&service=mail&sacu=1&rip=1&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
        driver.find_element(By.ID, 'identifierId').send_keys(
            email + Keys.RETURN)
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, '[name="password"]').send_keys(
            password + Keys.RETURN)
        # open first email
        time.sleep(3)
        driver.refresh()
        driver.switch_to.active_element
        time.sleep(2)
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[role="gridcell"]')))
        element.click()
        logging.info("First letter is opened")

    def checkVarInUrl(self, qsVar, expectedValue, url=None):
        if url is None:
            url = self.get_driver().current_url

        uri = urlparse(url)
        qs = parse_qs(uri.query)
        try:
            qs[qsVar] == expectedValue
        except KeyError:
            return False

    def search_product(self, search_query):
        logging.info("Try to search:", search_query)
        driver = self.get_driver()
        driver.find_element(By.CSS_SELECTOR, '[name="search_by"]').clear()
        driver.find_element(By.CSS_SELECTOR, '[name="search_by"]').send_keys(search_query)
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'submitButton')))
        element.click()
        logging.info("Search done")

    def logout(self):
        logging.debug("Attempt to logout")
        driver = self.get_driver()
        element = WebDriverWait(driver, self.DEFAULT_WAIT).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Logout')))
        element.click()
        time.sleep(1)
        assert not self.checkVarInUrl('mod', 'profile'), "Logout failed"

    def login_as_user(self, username="bizibitesting", password="q1q1q1q1", user_data=None):
        logging.debug("Attempt to login with credentials", username, password)

        driver = self.get_driver()

        # login in new account
        if not driver.find_element_by_id('login_modal_form').is_displayed():
            logging.warning('Trying to click signin')
            element = WebDriverWait(driver, self.DEFAULT_WAIT * 2).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'Sign In')))
            element.click()
            print('Click on the Sign In')

        # after clicking new sing up window is opened so we should jump to it

        driver.switch_to.active_element

        element = WebDriverWait(driver, self.DEFAULT_WAIT * 5).until(
            EC.element_to_be_clickable((By.ID, 'usernameFld')))
        element.clear()
        element.send_keys(username)

        element = WebDriverWait(driver, self.DEFAULT_WAIT * 5).until(
            EC.element_to_be_clickable((By.ID, 'passwordFld')))
        element.send_keys(password + Keys.RETURN)

        # assertion that first name, last name, email and phone the same that during the registaration
        if user_data:
            logging.debug("user_data was provided, will assert it's validity")

            element = WebDriverWait(driver, self.DEFAULT_WAIT).until(
                EC.element_to_be_clickable((By.ID, 'lnkToProfile')))
            element.click()

            # check that user data are equal to registered data
            all_user_data = driver.find_elements(
                By.CLASS_NAME, 'border-form-control')

            assert bool(all_user_data[0].get_attribute(
                "value") == user_data['first_name']), "First name is not the same as registered"
            assert all_user_data[1].get_attribute(
                "value") == user_data['last_name'], "Last name is not the same as registered"
            assert all_user_data[2].get_attribute(
                "value") == user_data['phone'], "Phone is not the same as registered"
            assert all_user_data[3].get_attribute(
                "value") == user_data['email'], "Email is not the same as registered"

            logging.debug(
                'ok -> assertion that first name, last name, email and phone matches data provided')
        return True

    def wait_for_el(self, selector):
        logging.debug("Wait for element")

        driver = self.get_driver()
        element = WebDriverWait(driver, self.DEFAULT_WAIT).until(
            EC.element_to_be_clickable(selector))
        return element

    def set_new_pass(self, new_pass):
        logging.debug("Change password")

        driver = self.get_driver()

        set_pass = self.wait_for_el((By.CSS_SELECTOR, '[name="password"]'))
        set_pass.send_keys(new_pass + Keys.RETURN)

        confirm_pass = self.wait_for_el(
            (By.CSS_SELECTOR, '[name="password2"]'))
        confirm_pass.send_keys(new_pass + Keys.RETURN)

        alert_text = self.wait_for_el((By.CLASS_NAME, 'text-success')).text
        assert alert_text == "Your password has been successfully updated", "Password is not updated"

    def count_items_in_card(self):
        logging.info("Cont items on the card")
        driver = self.get_driver()
        number = driver.find_element(By.ID, 'cart-item-count').text
        if number == '':
            return 0
        else:
            return int(number)

    def checkout(self, invoice=None, cancel=None):
        logging.info("Try to checkout with test credentials")
        if cancel:
            return False
        driver = self.driver
        time.sleep(self.TIME)
        old_url = driver.current_url
        card_number, CardExpDate, CardCVV2 = '4111111111111111', '1234', '123'

        element = self.wait_for_el((By.CSS_SELECTOR, '#paymentForm>iframe'))

        # frame = driver.find_element(By.CSS_SELECTOR, '#paymentForm>iframe')
        time.sleep(self.TIME)
        driver.switch_to.frame(element)

        id = self.wait_for_el(
            (By.XPATH, '/html/body/form/div/div[2]/div[2]/fieldset/*[@id="CardNo"]'))
        id.send_keys(card_number)

        ExpDate = self.wait_for_el((By.XPATH, '//*[@id="CardExpDate"]'))
        ExpDate.send_keys(CardExpDate)

        CVV2 = self.wait_for_el((By.XPATH, '//*[@id="CardCVV2"]'))
        CVV2.send_keys(CardCVV2)
        # BtnSubmit
        pay = self.wait_for_el((By.ID, 'BtnSubmit'))
        pay.click()

        if invoice:
            # RS check here
            max_wait = 120
            while max_wait >= 0:
                if driver.current_url != old_url:
                    time.sleep(5)
                    break
                max_wait -= 1
                time.sleep(1)

            driver.switch_to.default_content()
            elem = WebDriverWait(driver, 140).until(
                EC.presence_of_element_located((By.ID, 'generic-content-body')))

            html_text_inside = elem.get_attribute('innerHTML').strip()
            print(html_text_inside)
            assert "Thanks for your payment, below are the details for the transaction, we've also sent you a copy on email" in html_text_inside, "Invoice payment is not occurred"
        else:
            # assert
            driver.switch_to.default_content()
            elem = WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'text-success')))

            html_text_inside = elem.get_attribute('innerHTML').strip()

            assert 'Congrats! Your order number' in html_text_inside
            # continue shopping
            element = self.wait_for_el((By.CSS_SELECTOR, '.cart_navigation>a'))
            element.click()
