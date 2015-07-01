from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class UICheckException(Exception):
    def __init__(self, message):
        raise Exception(message)


class SeleniumApi(object):
    def __init__(self, driver):
        """

        :param driver: webdriver
        """
        assert isinstance(driver, webdriver.Firefox)
        self.driver = driver

    retry = 2
    timeout_to_locate_element_in_seconds = 20
    timeout_to_determine_visibility_in_seconds = 60
    timeout_to_determine_if_clickable_in_seconds = 20
    timeout_to_wait_for_text_in_seconds = 120
    implicit_wait_default_in_seconds = 30
    timeout_to_check_for_visibility_in_seconds = 3

    def set_implicit_wait(self, implicit_wait_time):
        """
        Sets implicit wait for webdriver
        :param implicit_wait_time:
        """
        self.driver.implicitly_wait(self, implicit_wait_time)

    def close_browser(self):
        """
        Closes firefox.
        """
        self.driver.quit()


    def get_url(self):
        """
        Returns currentv url.
        """
        url = self.driver.current_url.encode('ascii', 'ignore')
        url = str(url)
        return url

    def wait_for_element_present_by_id(self, element_id):
        """
        Waits for element to be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        """
        print "Executing wait_for_element_present_by_id('{0}')".format(element_id)
        print "Looking for element id = '{0}' in the DOM".format(element_id)
        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(EC.presence_of_element_located(
                (By.ID, element_id)))
            print "Found element by id = '{0}'".format(element_id)
        except NoSuchElementException, nse:
            print "Did not find element by id = '{0}'".format(element_id)
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by id = '{0}'.".format(element_id)

    def wait_for_element_present_by_css(self, css_selector):
        """
        Waits for element to be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        """
        print "Executing wait_for_element_present_by_css ('{0}')".format(css_selector)
        print "Looking for element by css = '{0}' in the DOM.".format(css_selector)
        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, css_selector)))
            print "Found element by css = '{0}'".format(css_selector)
        except NoSuchElementException, nse:
            print "Did not find element by css = '{0}'".format(css_selector)
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by css = '{0}'".format(css_selector)

    def wait_for_element_present_by_link_text(self, link_text):
        """
        Waits for element to be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        :param link_text:
        """
        print "Executing wait_for_element_present_by_link_text ('{0}')".format(link_text)
        print "Looking for element by link_text = '{0}' in the DOM.".format(link_text)
        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(EC.presence_of_element_located(
                (By.LINK_TEXT, link_text)))
            print "Found element by link_text = '{0}'".format(link_text)
        except NoSuchElementException, nse:
            print "Did not find element by link_text = '{0}'".format(link_text)
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by link_text = '{0}'".format(link_text)

    def wait_for_element_present_by_name(self, name):
        """
        Waits for element to be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        :param name:
        """
        print "Executing wait_for_element_present_by_name ('{0}')".format(name)
        print "Looking for element by name = '{0}' in the DOM.".format(name)
        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(EC.presence_of_element_located(
                (By.NAME, name)))
            print "Found element by name = '{0}'".format(name)
        except NoSuchElementException, nse:
            print "Did not find element by name = '{0}'".format(name)
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by name = '{0}'".format(name)

    def wait_for_visible_by_id(self, element_id, timeout_in_seconds=None):
        """
        Waits for the element to become visible. First, checks if element is present.
        :param timeout_in_seconds:
        :param element_id:
        """
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_determine_visibility_in_seconds

        print "Executing wait_for_visible_by_id('{0}'), timeout_in_seconds isb set to {1}".format(element_id, timeout_in_seconds)
        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(EC.visibility_of_element_located((By.ID, element_id)))
            print "Element by id = '{0}' was located in DOM and is visible.".format(element_id)
        except TimeoutException:
            print "ERROR: Timed out: element by id = '{0}' not visible.".format(element_id)
            print "Checking whether element by id = '{0}' present in the DOM.".format(element_id)
            try:
                self.driver.find_element_by_id(element_id)
                print "Element by id = '{0}' is present in the DOM but not visible.".format(element_id)
            except NoSuchElementException:
                print "ERROR: Element by id = '{0}' not found in the DOM.".format(element_id)
            return False

    def wait_for_visible_by_css(self, css, timeout_in_seconds=None):
        """
        Waits for the element to become visible. First, checks if element is present.
        :param timeout_in_seconds:
        :param css:
        """

        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_determine_visibility_in_seconds

        print "Executing wait_for_visible_by_css('{0}'), timeout_in_seconds is set to {1}".format(css, timeout_in_seconds)

        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
            print "Element by css = '{0}' was located in DOM and is visible.".format(css)
        except TimeoutException:
            print "ERROR: Timed out: element by css = '{0}' not visible.".format(css)
            print "Checking whether element by css = '{0}' present in the DOM.".format(css)
            try:
                self.driver.find_element_by_css_selector(css)
                print "Element by css = '{0}' is present in the DOM but not visible.".format(css)
            except NoSuchElementException:
                print "ERROR: Element by css = '{0}' not found in the DOM.".format(css)
            return False

    def wait_for_visible_by_xpath(self, xpath, timeout_in_seconds=None):
        """
        Waits for the element to become visible. First, checks if element is present.
        :param xpath:
        """

        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_determine_visibility_in_seconds

        print "Executing wait_for_visible_by_xpath('{0}'), timeout_in_seconds is set to {1}".format(xpath, timeout_in_seconds)

        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            print "Element by xpath = '{0}' was located in DOM and is visible.".format(xpath)
        except TimeoutException:
            print "ERROR: Timed out: element by xpath = '{0}' not visible.".format(xpath)
            print "Checking whether element by xpath = '{0}' present in the DOM.".format(xpath)
            try:
                self.driver.find_element_by_xpath(xpath)
                print "Element by xpath = '{0}' is present in the DOM but not visible.".format(xpath)
            except NoSuchElementException:
                print "ERROR: Element by xpath = '{0}' not found in the DOM.".format(xpath)
            return False

    def check_visibility_by_id(self, element_id):
        """
        Checks if the element is visible.
        :param element_id:
        """

        print "Executing check_visibility_by_id('{0}')".format(element_id)

        try:
            WebDriverWait(self.driver, self.timeout_to_check_for_visibility_in_seconds).until(EC.visibility_of_element_located((By.ID, element_id)))
            print "Element by id = '{0}' was located in DOM and is visible.".format(element_id)
            return True
        except TimeoutException:
            print "ERROR: Timed out: element by id = '{0}' not visible.".format(element_id)
            return False

    def check_visibility_by_css(self, css):
        """
        Checks if the element is visible.
        :param css:
        """

        print "Executing check_visibility_by_css('{0}')".format(css)

        try:
            WebDriverWait(self.driver, self.timeout_to_check_for_visibility_in_seconds).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
            print "Element by css = '{0}' was located in DOM and is visible.".format(css)
            return True
        except TimeoutException:
            print "Element by css = '{0}' not visible.".format(css)
            return False

    def wait_for_clickable_by_id(self, element_id):
        """
        Waits for an element to be present, visible and enabled such that you can click it.
        :param element_id:
        """
        print "Executing wait_for_clickable_by_id('{0}')".format(element_id)

        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(EC.element_to_be_clickable((By.ID, element_id)))
            print "Found clickable element by id = '{0}'".format(element_id)
        except TimeoutException, tout:
            print "ERROR: Did not find clickable element by id = '{0}'".format(element_id)
            print "Checking whether element by id = '{0}' present in the DOM.".format(element_id)
            try:
                self.driver.find_element_by_id(element_id)
                print "Element by id = '{0}' is present in the DOM but not clickable.".format(element_id)
            except NoSuchElementException:
                print "ERROR: Element by id = '{0}' not found in the DOM.".format(element_id)

    def wait_for_clickable_by_css(self, css):
        """
        Waits for an element to be present, visible and enabled such that you can click it.
        :param css:
        """
        print "Executing wait_for_clickable_by_css('{0}')".format(css)

        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
            print "Found clickable element by css = '{0}'".format(css)
        except TimeoutException, tout:
            print "ERROR: Did not find clickable element by css = '{0}'".format(css)
            print "Checking whether element by css = '{0}' present in the DOM.".format(css)
            try:
                self.driver.find_element_by_css_selector(css)
                print "Element by css = '{0}' is present in the DOM but not clickable.".format(css)
            except NoSuchElementException:
                print "ERROR: Element by css = '{0}' not found in the DOM.".format(css)

    def wait_for_clickable_by_xpath(self, xpath):
        """
        Waits for an element to be present, visible and enabled such that you can click it.
        :param xpath:
        """
        print "Executing wait_for_clickable_by_xpath('{0}')".format(xpath)

        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            print "Found clickable element by xpath = '{0}'".format(xpath)
        except TimeoutException, tout:
            print "ERROR: Did not find clickable element by xpath = '{0}'".format(xpath)
            print "Checking whether element by xpath = '{0}' present in the DOM.".format(xpath)
            try:
                self.driver.find_element_by_xpath(xpath)
                print "Element by css = '{0}' is present in the DOM but not clickable.".format(xpath)
            except NoSuchElementException:
                print "ERROR: Element by css = '{0}' not found in the DOM.".format(xpath)

    def click_element_by_id(self, element_id):
        """
        Waits for an element to be present and visible such that you can click it.
        Clicks the element.
        :param element_id:
        """
        self.wait_for_visible_by_id(element_id)
        print "Executing click_element_by_id('{0}')".format(element_id)
        try:
            self.driver.find_element_by_id(element_id).click()
            print "Clicking on element by id = ('{0}')".format(element_id)
        except Exception, e:
            print "ERROR: Could not perform click on element by id = ('{0}')".format(element_id)
            self.close_browser()
            raise

    def click_element_by_css(self, css):
        """
        Waits for an element to be present and visible such that you can click it.
        Clicks the element.
        :param css:
        """
        self.wait_for_visible_by_css(css)
        print "Executing click_element_by_css('{0}')".format(css)
        try:
            self.driver.find_element_by_css_selector(css).click()
            print "Clicking on element by css = ('{0}')".format(css)
        except Exception, e:
            print "ERROR: Could not perform click on element by css = ('{0}')".format(css)
            self.close_browser()
            raise

    def wait_for_element_not_present_by_id(self, element_id):
        """
        Waits for element to NOT be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        :param element_id:
        """
        print "Executing wait_for_element_not_present_by_id('{0}')".format(element_id)
        print "Looking for element id = '{0}' in the DOM".format(element_id)
        self.set_implicit_wait(5)
        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until_not(
                EC.presence_of_element_located((By.ID, element_id)))
            print "Verified element by id = '{0}' not in the DOM".format(element_id)
        #except Exception, e:
        #    print "ERROR: Can not verify the element by id = '{0}' is not in the DOM".format(element_id)
        except TimeoutException, t:
            print "ERROR: Timed out. Element by id = '{0}' still found in the DOM.".format(element_id)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def wait_for_element_not_present_by_css(self, css):
        """
        Waits for element to NOT be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        :param css:
        """
        print "Executing wait_for_element_not_present_by_css('{0}')".format(css)
        print "Looking for element css = '{0}' in the DOM".format(css)
        self.set_implicit_wait(5)
        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, css)))
            print "Verified element by css = '{0}' not in the DOM".format(css)
        #except Exception, e:
        #    print "ERROR: Can not verify the element by id = '{0}' is not in the DOM".format(element_id)
        except TimeoutException, t:
            print "ERROR: Timed out. Element by css = '{0}' still found in the DOM.".format(css)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def wait_for_text_present_by_id(self, element_id, text, timeout_in_seconds=None):
        """
        Waits for text to be present.
        :param element_id:
        :param text:
        """
        self.set_implicit_wait(0)
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_wait_for_text_in_seconds

        print "Executing wait_for_text_present_by_id id = '{0}', text = '{1}'".format(element_id, text)
        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(
                EC.text_to_be_present_in_element((By.ID, element_id), text))
            print "Verified text {0} present in element by id = {1}".format(text, element_id)

        except TimeoutException, t:
            print "ERROR: Timed out. Could not verify presence of text = '{1}' in element by id = '{0}' timeout_in_seconds = {2}".format(element_id, text, timeout_in_seconds)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def wait_for_text_present_by_xpath(self, xpath, text, timeout_in_seconds=None):
        """
        Waits for text to be present.
        :param xpath:
        :param text:
        """
        self.set_implicit_wait(0)
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_wait_for_text_in_seconds

        print "Executing wait_for_text_present_by_xpath xpath = '{0}', text = '{1}', timeout_in_seconds = {2}".format(xpath, text, timeout_in_seconds)
        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(
                EC.text_to_be_present_in_element((By.XPATH, xpath), text))
            print "Verified text {0} present in element by xpath = {1}".format(text, xpath)

        except TimeoutException, t:
            print "ERROR: Timed out. Could not verify presence of text = '{1}' in element by xpath = '{0}'".format(xpath, text)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)


    def wait_for_text_present_by_css(self, css, text, timeout_in_seconds=None):
        """
        Waits for text to be present.
        :param css:
        :param text:
        """
        self.set_implicit_wait(0)
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_wait_for_text_in_seconds
        print "Executing wait_for_text_present_by_css css = '{0}', text = '{1}', timeout_in_seconds = {2}".format(css, text, timeout_in_seconds)
        text_present = self.store_text_by_css(css)
        print "Text present: "+text_present
        try:
            WebDriverWait(self.driver, self.timeout_to_wait_for_text_in_seconds).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, css), text))
            print "Verified text {0} present in element by id = {1}".format(text, css)

        except TimeoutException, t:
            print "ERROR: Timed out. Could not verify presence of text = '{1}' in element by css = '{0}'".format(css, text)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)
        text_present=self.store_text_by_css(css)
        print "Text present: "+text_present

    def wait_for_text_not_present_by_id(self, element_id, text):
        """
        Waits for text to be not present.
        """
        self.set_implicit_wait(5)
        print "Executing wait_for_text_not_present_by_id id = '{0}', text = '{1}'".format(element_id, text)
        try:
            WebDriverWait(self.driver, self.timeout_to_wait_for_text_in_seconds).until_not(
                EC.text_to_be_present_in_element((By.ID, element_id), text))
            print "Verified text {0} not present in element by id = {1}".format(text, element_id)

        except TimeoutException, t:
            print "ERROR: Timed out. Could not verify text = '{1}' not present in element by id = '{0}'".format(element_id, text)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def wait_for_text_not_present_by_css(self, css, text):
        """
        Waits for text to be not present.
        :param css:
        :param text:
        """
        self.set_implicit_wait(5)
        print "Executing wait_for_text_not_present_by_css css = '{0}', text = '{1}'".format(css, text)
        try:
            WebDriverWait(self.driver, self.timeout_to_wait_for_text_in_seconds).until_not(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, css), text))
            print "Verified text {0} not present in element by css = {1}".format(text, css)

        except TimeoutException, t:
            print "ERROR: Timed out. Could not verify text = '{1}' not present in element by css = '{0}'".format(css, text)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def send_keys_by_id(self, element_id, text):
        """
        Simulates user typing text input.
        :param element_id:
        :param text:
        """
        print "Executing send_keys_by_id id={0}, text={1}".format(element_id, text)
        self.wait_for_visible_by_id(element_id)
        print "Clearing field by if = '{0}'".format(element_id)
        self.driver.find_element_by_id(element_id).clear()
        print "Typing text '{1}' into field by id = '{0}'".format(element_id, text)
        self.driver.find_element_by_id(element_id).send_keys(text)

    def send_keys_by_css(self, css, text):
        """
        Simulates user typing text input.
        :param css:
        :param text:
        """
        print "Executing send_keys_by_css css={0}, text={1}".format(css, text)
        self.wait_for_visible_by_css(css)
        print "Clearing field by css = '{0}'".format(css)
        self.driver.find_element_by_css_selector(css).clear()
        print "Typing text '{1}' into field by css = '{0}'".format(css, text)
        self.driver.find_element_by_css_selector(css).send_keys(text)

    def send_keys_by_xpath(self, xpath, text):
        """
        Simulates user typing text input.
        :param xpath:
        :param text:
        """
        print "Executing send_keys_by_xpath xpath={0}, text={1}".format(xpath, text)
        self.wait_for_visible_by_xpath(xpath)
        print "Clearing field by xpath = '{0}'".format(xpath)
        self.driver.find_element_by_xpath(xpath).clear()
        print "Typing text '{1}' into field by xpath = '{0}'".format(xpath, text)
        self.driver.find_element_by_xpath(xpath).send_keys(text)

    def store_text_by_id(self, element_id):
        """
        Stores visible text.
        :param element_id:
        """
        print "Executing store_text_by_id('{0}')".format(element_id)
        self.wait_for_visible_by_id(element_id)
        print "Getting text by id = '{0}'".format(element_id)
        return self.driver.find_element_by_id(element_id).text

    def store_text_by_css(self, css):
        """
        Stores visible text.
        :param css:
        """
        print "Executing store_text_by_css('{0}')".format(css)
        self.wait_for_visible_by_css(css)
        print "Getting text by css = '{0}'".format(css)
        return self.driver.find_element_by_css_selector(css).text


    def store_text_by_xpath(self, xpath):
        """
        Stores visible text.
        :param xpath:
        """
        print "Executing store_text_by_xpath('{0}')".format(xpath)
        self.wait_for_visible_by_xpath(xpath)
        print "Getting text by xpath = '{0}'".format(xpath)
        return self.driver.find_element_by_xpath(xpath).text


    def select_by_id(self, element_id, text):
        """
        Selects element with particular text on it.
        :param element_id:
        :param text:
        """
        print "Executing select_by_id id = {0}, text = {1}".format(element_id, text)
        self.wait_for_text_present_by_id(element_id, text)
        print "Selecting element with text = {1} by id = {0}".format(element_id, text)
        Select(self.driver.find_element_by_id(element_id)).select_by_visible_text(text)

    def select_by_css(self, css, text):
        """
        Selects element with particular text on it.
        :param css:
        :param text:
        """
        print "Executing select_by_id css = {0}, text = {1}".format(css, text)
        self.wait_for_text_present_by_css(css, text)
        print "Selecting element with text = {1} by css = {0}".format(css, text)
        Select(self.driver.find_element_by_css_selector(css)).select_by_visible_text(text)

    def select_by_link_text(self, link_text, text):
        """
        Selects element with particular text on it.
        :param link_text:
        :param text:
        """
        self.wait_for_element_present_by_link_text(text)
        print "Selecting element with text = {1} by link_text = {0}".format(link_text, text)
        Select(self.driver.find_element_by_link_text(link_text)).select_by_visible_text(text)

    def select_by_name_and_value(self, name, value):
        """
        Selects element by name and value.
        :param name:
        :param text:
        """
        self.wait_for_element_present_by_name(name)
        print "Selecting element with value = {1} by name = {0}".format(name, value)
        Select(self.driver.find_element_by_name(name)).select_by_value(value)

    def get_attrubute_by_css(self, css, attribute_name):
        """
        Finds element by css. Returns specified attribute.
        :param css:
        :param attribute_name:
        """
        element = self.driver.find_element_by_css_selector(css)
        attribute = element.get_attribute(attribute_name)
        print attribute
        return attribute

    def get_attrubute_by_id(self, element_id, attribute_name):
        """
        Finds element by id. Returns specified attribute.
        :param element_id:
        :param attribute_name:
        """
        element = self.driver.find_element_by_id(element_id)
        attribute = element.get_attribute(attribute_name)
        print attribute
        return attribute

    def get_attrubute_by_xpath(self, xpath, attribute_name):
        """
        Finds element by xpath. Returns specified attribute.
        :param xpath:
        :param attribute_name:
        """
        element = self.driver.find_element_by_xpath(xpath)
        attribute = element.get_attribute(attribute_name)
        print attribute
        return attribute