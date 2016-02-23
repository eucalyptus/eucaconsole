import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


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

    retry = 3
    timeout_to_locate_element_in_seconds = 60
    timeout_to_determine_visibility_in_seconds = 120
    timeout_to_determine_if_clickable_in_seconds = 120
    timeout_to_wait_for_text_in_seconds = 240
    implicit_wait_default_in_seconds = 120
    timeout_to_check_for_visibility_in_seconds = 10

    def set_implicit_wait(self, implicit_wait_time):
        """
        Sets implicit wait for webdriver
        :param implicit_wait_time:
        """
        self.driver.implicitly_wait(implicit_wait_time)

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

    def is_clickable_by_id(self, element_id):
        """

        :param element_id:
        """
        element = self.driver.find_element_by_id(element_id)
        return element.is_enabled()

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
            raise
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by id = '{0}'.".format(element_id)
            raise

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
            raise
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by css = '{0}'".format(css_selector)
            raise

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
            raise
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by link_text = '{0}'".format(link_text)
            raise

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
            raise
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by name = '{0}'".format(name)
            raise

    def wait_for_visible_by_id(self, element_id, timeout_in_seconds=None):
        """
        Waits for the element to become visible. First, checks if element is present. Does not raise Error on exception!
        :param timeout_in_seconds:
        :param element_id:
        """
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_determine_visibility_in_seconds

        print "Executing wait_for_visible_by_id('{0}'), timeout_in_seconds is set to {1}".format(
            element_id, timeout_in_seconds)
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

        print "Executing wait_for_visible_by_css('{0}'), timeout_in_seconds is set to {1}".format(css,
                                                                                                  timeout_in_seconds)

        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
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
        except Exception, e:
            print "ERROR: Unknown Exception e thrown by webdriver."
            print "Element was not found"
            pass

    def wait_for_visible_by_xpath(self, xpath, timeout_in_seconds=None):
        """
        Waits for the element to become visible. First, checks if element is present.
        :param xpath:
        """

        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_determine_visibility_in_seconds

        print "Executing wait_for_visible_by_xpath('{0}'), timeout_in_seconds is set to {1}".format(xpath,
                                                                                                    timeout_in_seconds)

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

    def verify_visible_by_id(self, element_id, timeout_in_seconds=None):
        """
        Waits for the element to become visible. First, checks if element is present. Raises Error on exception.
        :param timeout_in_seconds:
        :param element_id:
        """
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_determine_visibility_in_seconds

        print "Executing verify_visible_by_id('{0}'), timeout_in_seconds is set to {1}".format(
            element_id, timeout_in_seconds)
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
                raise
            raise

    def verify_visible_by_css(self, css, timeout_in_seconds=None):
        """
        Waits for the element to become visible. First, checks if element is present. Raises Error on exception.
        :param timeout_in_seconds:
        :param css:
        """

        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_determine_visibility_in_seconds

        print "Executing verify_visible_by_css('{0}'), timeout_in_seconds is set to {1}".format(css,
                                                                                           timeout_in_seconds)

        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
            print "Element by css = '{0}' was located in DOM and is visible.".format(css)
        except TimeoutException:
            print "ERROR: Timed out: element by css = '{0}' not visible.".format(css)
            print "Checking whether element by css = '{0}' present in the DOM.".format(css)
            try:
                self.driver.find_element_by_css_selector(css)
                print "Element by css = '{0}' is present in the DOM but not visible.".format(css)
            except NoSuchElementException:
                print "ERROR: Element by css = '{0}' not found in the DOM.".format(css)
                raise
            raise
        except Exception, e:
            print "ERROR: Unknown Exception e thrown by webdriver."
            print "Element was not found"
            raise

    def verify_visible_by_xpath(self, xpath, timeout_in_seconds=None):
        """
        Waits for the element to become visible. First, checks if element is present. Raises Error on exception.
        :param xpath:
        """

        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_determine_visibility_in_seconds

        print "Executing verify_visible_by_xpath('{0}'), timeout_in_seconds is set to {1}".format(xpath,
                                                                                                    timeout_in_seconds)

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
                raise
            raise

    def check_visibility_by_id(self, element_id):
        """
        Checks if the element is visible.
        :param element_id:
        """

        print "Executing check_visibility_by_id('{0}')".format(element_id)

        try:
            self.set_implicit_wait(1)
            WebDriverWait(self.driver, self.timeout_to_check_for_visibility_in_seconds).until(
                EC.visibility_of_element_located((By.ID, element_id)))
            self.set_implicit_wait(self.implicit_wait_default_in_seconds)
            print "Element by id = '{0}' was located in DOM and is visible.".format(element_id)
            return True
        except TimeoutException:
            print "Element by id = '{0}' not visible.".format(element_id)
            return False

    def check_visibility_by_css(self, css):
        """
        Checks if the element is visible.
        :param css:
        """

        print "Executing check_visibility_by_css('{0}')".format(css)

        try:
            self.set_implicit_wait(0)
            WebDriverWait(self.driver, self.timeout_to_check_for_visibility_in_seconds).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
            self.set_implicit_wait(self.implicit_wait_default_in_seconds)
            print "Element by css = '{0}' was located in DOM and is visible.".format(css)
            return True
        except TimeoutException:
            print "Element by css = '{0}' not visible.".format(css)
            return False

    def verify_selected_by_id(self, element_id):
        """
        Checks if element is selected.
        :param element_id:
        """
        is_selected = self.driver.execute_script(("return document.getElementById('%s').checked") % element_id)
        return is_selected

    def wait_for_enabled_by_id(self, element_id):
        """
        Waits for an element to be present, visible and enabled such that you can click it.
        :param element_id:
        """
        print "Executing wait_for_clickable_by_id('{0}')".format(element_id)

        try:
            for i in range(1, 20):
                element=self.driver.find_element_by_id(element_id)
                if element.is_enabled():
                    print "Element by id = " + element_id + " is enabled "
                    time.sleep(1)
                    break
                else:
                    print "Waiting for element by id = " + element_id + " to become enabled "
        except TimeoutException:
            print "Element by id = '{0}' not enabled.".format(element_id)
            return False

    def verify_enabled_by_css(self, css):
        """
        Waits for an element to become enabled.
        :param css:
        """
        print "Checking if element by_css ('{0}') is enabled".format(css)

        try:
            for i in range(1, 30):
                element = self.driver.find_element_by_css_selector(css)
                if element.is_enabled():
                    print "Element by css = " + css + " is enabled "
                    time.sleep(1)
                    break
                else:
                    print "Waiting for element by css = " + css + " to become enabled "
        except TimeoutException:
            print "Element by icss = '{0}' not enabled.".format(css)
            return False

    def wait_for_clickable_by_id(self, element_id):
        """
        Waits for an element to be present, visible and enabled such that you can click it.
        :param element_id:
        """
        print "Executing wait_for_clickable_by_id('{0}')".format(element_id)

        try:
            self.set_implicit_wait(0)
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(
                EC.element_to_be_clickable((By.ID, element_id)))
            self.set_implicit_wait(self.implicit_wait_default_in_seconds)
            print "Found clickable element by id = '{0}'".format(element_id)
        except TimeoutException, tout:
            print "ERROR: Did not find clickable element by id = '{0}'".format(element_id)
            print "Checking whether element by id = '{0}' present in the DOM.".format(element_id)
            try:
                self.driver.find_element_by_css_selector(element_id)
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
            self.set_implicit_wait(0)
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
            self.set_implicit_wait(self.implicit_wait_default_in_seconds)
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
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
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
        self.wait_for_clickable_by_id(element_id)
        print "Executing click_element_by_id('{0}')".format(element_id)
        try:
            time.sleep(0.6)
            self.driver.find_element_by_id(element_id).click()
            print "Clicking on element by id = ('{0}')".format(element_id)
        except Exception, e:
            print "ERROR: Could not perform click on element by id = ('{0}')".format(element_id)
            self.close_browser()
            raise

    def click_element_by_css(self, css, wait=True):
        """
        Waits for an element to be present and visible such that you can click it.
        Clicks the element.
        :param css:
        """
        if wait:
            self.wait_for_clickable_by_css(css)
        print "Executing click_element_by_css('{0}')".format(css)
        try:
            time.sleep(0.6)
            self.driver.find_element_by_css_selector(css).click()
            print "Clicking on element by css = ('{0}')".format(css)
        except Exception, e:
            print "ERROR: Could not perform click on element by css = ('{0}')".format(css)
            self.close_browser()
            raise

    def click_element_by_id_robust(self, element_id, element_id_on_next_page):
        """
        Waits for an element to be enabled such that you can click it.
        Clicks the element, checks if element is still visible, hits enter on element if visible up to 5 times.
        :param element_id_on_next_page:
        :param element_id:
        """
        print "Executing click_element_by_id_robust ('{0}')".format(element_id)
        self.wait_for_clickable_by_id(element_id)
        time.sleep(2)
        self.click_element_by_id(element_id)
        time.sleep(2)

        is_visible = self.check_visibility_by_id(element_id_on_next_page)
        k = 1
        while not is_visible and (k < 6):
            try:
                time.sleep(2)
                print "Hitting enter. Executing attempt " + str(k)
                self.send_keys_by_id(element_id, "\n", clear_field=False)
            except Exception, e:
                print str(k) + "-th attempt to hit enter unsuccessful."
            is_visible = self.check_visibility_by_id(element_id_on_next_page)
            k = k + 1

    def click_element_by_id_css_robust(self, element_id, element_css_on_next_page):
        """
        Waits for an element to be enabled such that you can click it.
        Clicks the element, checks if element is still visible, hits enter on element if visible up to 5 times.
        :param element_css_on_next_page:
        :param element_id:
        """
        print "Executing click_element_by_id_css_robust ('{0}')".format(element_id)
        self.wait_for_clickable_by_id(element_id)
        time.sleep(2)
        self.click_element_by_id(element_id)
        time.sleep(2)

        is_visible = self.check_visibility_by_css(element_css_on_next_page)
        k = 1
        while not is_visible and (k < 6):
            try:
                time.sleep(2)
                print "Hitting enter. Executing attempt " + str(k)
                self.send_keys_by_id(element_id, "\n", clear_field=False)
            except Exception, e:
                print str(k) + "-th attempt to hit enter unsuccessful."
            is_visible = self.check_visibility_by_css(element_css_on_next_page)
            k = k + 1

    def click_element_by_id_text_by_id_robust(self, element_id, element_id_for_text_on_next_page, text):
        """
        Waits for an element to be enabled such that you can click it.
        Clicks the element, checks if text is visible, hits enter on element if visible up to 5 times.
        :param element_css_on_next_page:
        :param element_id:
        """
        print "Executing click_element_by_id_css_robust ('{0}')".format(element_id)
        self.wait_for_clickable_by_id(element_id)
        self.click_element_by_id(element_id)
        is_visible = self.check_visibility_by_id(element_id_for_text_on_next_page)
        print "Checked visibility on {0}".format(element_id_for_text_on_next_page) + "Visibility status: " + str(
            is_visible)
        k = 1
        no_match = True
        while no_match and (k < 6):
            if is_visible:
                title = self.store_text_by_id(element_id_for_text_on_next_page)
                print "Stored text at the locator {0} ".format(element_id_for_text_on_next_page) + title
                try:
                    if title == text:
                        no_match = False

                    else:
                        time.sleep(1)
                        print "Hitting enter. Executing attempt " + str(k)
                        try:
                            self.send_keys_by_id(element_id, "\n", clear_field=False)
                        except Exception, e:
                            print str(k) + "-th attempt to hit enter unsuccessful."
                        is_visible = self.check_visibility_by_id(element_id_for_text_on_next_page)

                        print "Checked visibility on {0}".format(
                            element_id_for_text_on_next_page) + "Visibility status: " + str(is_visible)
                        k = k + 1
                except:
                    pass
            else:
                time.sleep(1)
                print "Hitting enter. Executing attempt " + str(k)
                try:
                    self.send_keys_by_id(element_id, "\n", clear_field=False)
                except Exception, e:
                    print str(k) + "-th attempt to hit enter unsuccessful."
                is_visible = self.check_visibility_by_id(element_id_for_text_on_next_page)
                print "Checked visibility on {0}".format(
                    element_id_for_text_on_next_page) + "Visibility status: " + str(is_visible)
                k = k + 1

    def click_element_by_css_robust(self, css, element_css_on_next_page):
        """
        Waits for an element to be enabled such that you can click it.
        Clicks the element, checks if element is still visible, hits enter on element if visible up to 5 times.
        :param element_id:
        """
        print "Executing click_element_by_css_robust ('{0}')".format(css)
        self.wait_for_clickable_by_css(css)
        time.sleep(1)
        self.click_element_by_css(css)
        time.sleep(1)

        is_visible = self.check_visibility_by_css(element_css_on_next_page)
        print "Checked visibility on {0}".format(element_css_on_next_page) + "Visibility status: " + str(is_visible)
        k = 1
        while not is_visible and (k < 6):
            print "Executing Attempt {0}".format(k)
            print""
            try:
                time.sleep(2)
                is_visible = self.check_visibility_by_css(css)
                if is_visible:
                    break
                time.sleep(1)
                print "Hitting enter. Executing attempt " + str(k)
                self.send_keys_by_id(css, "\n", clear_field=False)
            except NoSuchElementException:
                print "Element by css = {0} not found".format(css)
            except ElementNotVisibleException:
                print "Element by css = {0} not visible".format(css)
            except Exception, e:
                print str(k) + "-th attempt to hit enter unsuccessful."
                raise
            is_visible = self.check_visibility_by_css(element_css_on_next_page)
            print "Checked visibility on {0}".format(element_css_on_next_page) + "Visibility status: " + str(is_visible)
            k = k + 1

        while not is_visible and (k < 8):
            try:
                time.sleep(2)
                is_visible = self.check_visibility_by_css(css)
                if is_visible:
                    break
                print "Hitting enter. Executing attempt " + str(k)
                self.send_keys_by_css(css, "\n", clear_field=False)
            except Exception, e:
                print str(k) + "-th attempt to hit enter unsuccessful."
                self.close_browser()
                raise
            is_visible = self.check_visibility_by_css(element_css_on_next_page)
            k = k + 1
            try:
                is_visible
            except Exception, e:
                print "ERROR: click_robust_by_css on element by css={0} has failed.".format(css)
                self.close_browser()
                raise

    def click_element_by_id_resilient(self, element_id, element_to_disappear_id):
        """
        Method will verify that element is enabled and try performing a click and hit enter until given element disappears.
        """
        print "Executing click_element_by_id_resilient ('{0}')".format(element_id)
        #self.verify_enabled_by_id(element_id)
        self.wait_for_clickable_by_id(element_id)
        element = self.driver.find_element_by_id(element_id)
        element.click()
        is_visible = self.check_visibility_by_id(element_to_disappear_id)
        k = 1
        while is_visible and (k < 4):
            print "Repeated click. Executing attempt " + str(k)
            try:
                element.click()
            except Exception, e:
                print str(k) + "-th attempt to click unsuccessful."
                self.close_browser()
                raise
            time.sleep(1)
            is_visible = self.check_visibility_by_id(element_to_disappear_id)
            k = k + 1
        while is_visible and (k < 7):
            print "Hitting enter. Executing attempt " + str(k)
            try:
                self.send_keys_by_id(element_id, "\n", clear_field=False)
            except Exception, e:
                print str(k) + "-th attempt to hit enter unsuccessful."
                self.close_browser()
                raise
            time.sleep(1)
            is_visible = self.check_visibility_by_id(element_to_disappear_id)
            k = k + 1
        try:
            is_visible
        except Exception, e:
            print "ERROR: click_by_id_resilient on element by id={0} has failed.".format(element_id)
            self.close_browser()
            raise

    def click_element_by_css_resilient(self, css, element_to_disappear_css):
        """
        Method will verify that element is enabled and try performing a click and hit enter until given element disappears. Repeats attempts, does not raise exception.
        """
        print "Executing click_element_by_css_resilient ('{0}')".format(css)
        self.wait_for_clickable_by_css(css)
        element = self.driver.find_element_by_css_selector(css)
        element.click()
        is_visible = self.check_visibility_by_css(element_to_disappear_css)
        k = 1
        while is_visible and (k < 4):
            print "Repeated click. Executing attempt " + str(k)
            try:
                element.click()
            except Exception, e:
                print "ERROR: " + str(k) + "-th attempt to click unsuccessful."
                pass
            time.sleep(1)
            is_visible = self.check_visibility_by_css(element_to_disappear_css)
            k = k + 1
        while is_visible and (k < 7):
            print "Hitting enter. Executing attempt " + str(k)
            try:
                self.send_keys_by_css(css, "\n", clear_field=False)
            except Exception, e:
                print "ERROR: " + str(k) + "-th attempt to hit enter unsuccessful."
                pass
            time.sleep(1)
            is_visible = self.check_visibility_by_css(element_to_disappear_css)
            k = k + 1
        try:
            is_visible
        except Exception, e:
            print "ERROR: click_by_id_resilient on element by id={0} has failed.".format(css)
            pass

    def hover_by_id(self, element_id):
        """
        Goes to the element by id and hovers.
        """

        print "Executing hover over element by id = {0}".format(element_id)
        element = self.driver.find_element_by_id(element_id)
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

    def click_element_by_id_covert(self, element_id):
        """
        Waits for an element to be visible and clicks if it can.
        Clicks the element.
        :param element_id:
        """
        self.wait_for_visible_by_id(element_id)
        print "Executing click_element_by_id_covert ('{0}')".format(element_id)
        try:
            self.driver.find_element_by_id(element_id).click()
            print "Clicking on element by id = ('{0}')".format(element_id)
        except ElementNotVisibleException:
            print "ERROR: element by  by id = ('{0}') not visible".format(element_id)
            pass
        except Exception, e:
            print "ERROR: Could not perform click_on_element_covert by id = ('{0}')".format(element_id)
            pass

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
        except TimeoutException:
            print "ERROR: Timed out. Element by id = '{0}' still found in the DOM.".format(element_id)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def wait_for_element_not_present_by_css(self, css, timeout_in_seconds=None):
        """
        Waits for element to NOT be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        :param css:
        """
        print "Executing wait_for_element_not_present_by_css('{0}')".format(css)
        print "Looking for element css = '{0}' in the DOM".format(css)
        self.set_implicit_wait(5)
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_locate_element_in_seconds
        try:
            WebDriverWait(self.driver, timeout_in_seconds).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, css)))
            print "Verified element by css = '{0}' not in the DOM".format(css)
        #except Exception, e:
        #    print "ERROR: Can not verify the element by id = '{0}' is not in the DOM".format(element_id)
        except TimeoutException:
            print "ERROR: Timed out. Element by css = '{0}' still found in the DOM.".format(css)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def wait_for_text_present_by_id(self, element_id, text, timeout_in_seconds=None):
        """
        Waits for text to be present.
        :param timeout_in_seconds:
        :param element_id:
        """
        #self.set_implicit_wait(0)
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_wait_for_text_in_seconds

        print "Executing wait_for_text_present_by_id id = '{0}', text = '{1}'".format(element_id, text)
        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(
                EC.text_to_be_present_in_element((By.ID, element_id), text))
            print "Verified text {0} present in element by id = {1}".format(text, element_id)

        except TimeoutException:
            print "ERROR: Timed out. Could not verify presence of text = '{1}' in element by id = '{0}' " \
                  "timeout_in_seconds = {2}".format(element_id, text, timeout_in_seconds)
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

        print "Executing wait_for_text_present_by_xpath xpath = '{0}', text = '{1}', timeout_in_seconds = {2}".format(
            xpath, text, timeout_in_seconds)
        try:
            WebDriverWait(self.driver, timeout_in_seconds).until(
                EC.text_to_be_present_in_element((By.XPATH, xpath), text))
            print "Verified text {0} present in element by xpath = {1}".format(text, xpath)

        except TimeoutException:
            print "ERROR: Timed out. Could not verify presence of text = '{1}' in element by xpath = '{0}'".format(
                xpath, text)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def wait_for_text_present_by_css(self, css, text, timeout_in_seconds=None):
        """
        Waits for text to be present.
        :param timeout_in_seconds:
        :param css:
        :param text:
        """
        self.set_implicit_wait(0)
        if timeout_in_seconds is None:
            timeout_in_seconds = self.timeout_to_wait_for_text_in_seconds
        print "Executing wait_for_text_present_by_css css = '{0}', text = '{1}', " \
              "timeout_in_seconds = {2}".format(css, text, timeout_in_seconds)
        text_present = self.store_text_by_css(css)
        print "Text present: " + text_present
        try:
            WebDriverWait(self.driver, self.timeout_to_wait_for_text_in_seconds).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, css), text))
            print "Verified text {0} present in element by id = {1}".format(text, css)

        except TimeoutException:
            print "ERROR: Timed out. Could not verify presence of text = '{1}' in element by css = '{0}'".format(css,
                                                                                                                 text)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)
        text_present = self.store_text_by_css(css)
        print "Text present: " + text_present

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

        except TimeoutException:
            print "ERROR: Timed out. Could not verify text = '{1}' not present in element by id = '{0}'".format(
                element_id, text)
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

        except TimeoutException:
            print "ERROR: Timed out. Could not verify text = '{0}' not present in element by css = '{1}'".format(text,
                                                                                                                 css)
        self.set_implicit_wait(self.implicit_wait_default_in_seconds)

    def send_keys_by_id(self, element_id, text, clear_field=True):
        """
        Simulates user typing text input.
        :param element_id:
        :param text:
        """
        print "Executing send_keys_by_id id={0}, text={1}".format(element_id, text)
        self.wait_for_visible_by_id(element_id)
        if clear_field:
            print "Clearing field by if = '{0}'".format(element_id)
            time.sleep(0.6)
            self.driver.find_element_by_id(element_id).clear()
            time.sleep(0.6)
        print "Typing text '{1}' into field by id = '{0}'".format(element_id, text)
        self.driver.find_element_by_id(element_id).send_keys(text)

    def send_keys_by_css(self, css, text, clear_field=True):
        """
        Simulates user typing text input.
        :param css:
        :param text:
        """
        print "Executing send_keys_by_css css={0}, text={1}".format(css, text)
        self.wait_for_visible_by_css(css)
        if clear_field:
            print "Clearing field by css = '{0}'".format(css)
            self.driver.find_element_by_css_selector(css).clear()
        print "Typing text '{1}' into field by css = '{0}'".format(css, text)
        self.driver.find_element_by_css_selector(css).send_keys(text)

    def send_keys_by_xpath(self, xpath, text, clear_field=True):
        """
        Simulates user typing text input.
        :param xpath:
        :param text:
        """
        print "Executing send_keys_by_xpath xpath={0}, text={1}".format(xpath, text)
        self.wait_for_visible_by_xpath(xpath)
        if clear_field:
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

    def select_by_id(self, element_id, text='', index=-1, timeout_in_seconds=None):
        """
        Selects element with particular text on it.
        :param element_id:
        :param text:
        """
        print "Executing select_by_id id = {0}, text = {1}".format(element_id, text)
        self.wait_for_text_present_by_id(element_id, text, timeout_in_seconds=timeout_in_seconds)
        if index == -1:
            print "Selecting element with text = {1} by id = {0}".format(element_id, text)
            Select(self.driver.find_element_by_id(element_id)).select_by_visible_text(text)
        else:
            print "Selecting element with index = {1} by id = {0}".format(element_id, index)
            Select(self.driver.find_element_by_id(element_id)).select_by_index(index)

    def select_by_css(self, css, text='', index=-1):
        """
        Selects element with particular text on it.
        :param css:
        :param text:
        """
        print "Executing select_by_id css = {0}, text = {1}".format(css, text)
        self.wait_for_text_present_by_css(css, text)
        if index == -1:
            print "Selecting element with text = {1} by css = {0}".format(css, text)
            Select(self.driver.find_element_by_css_selector(css)).select_by_visible_text(text)
        else:
            print "Selecting element with index = {1} by css = {0}".format(css, index)
            Select(self.driver.find_element_by_css_selector(css)).select_by_index(index)

    def select_by_link_text(self, link_text, text='', index=-1):
        """
        Selects element with particular text on it.
        :param link_text:
        :param text:
        """
        self.wait_for_element_present_by_link_text(text)
        if index == -1:
            print "Selecting element with text = {1} by link_text = {0}".format(link_text, text)
            Select(self.driver.find_element_by_link_text(link_text)).select_by_visible_text(text)
        else:
            print "Selecting element with index = {1} by link_text = {0}".format(link_text, index)
            Select(self.driver.find_element_by_link_text(link_text)).select_by_index(index)

    def select_by_name_and_value(self, name, value):
        """
        Selects element by name and value.
        :param name:
        :param value:
        """
        self.wait_for_element_present_by_name(name)
        print "Selecting element with value = {1} by name = {0}".format(name, value)
        Select(self.driver.find_element_by_name(name)).select_by_value(value)

    def select_by_id_and_value(self, element_id, option_value):
        """
        Select an option by value
        :param element_id: The id attribute of the select element
        :param option_value: the option value to select
        """
        self.wait_for_element_present_by_id(element_id)
        print "Selecting element {0} with value = {1}".format(element_id, option_value)
        Select(self.driver.find_element_by_id(element_id)).select_by_value(option_value)

    def get_attribute_by_css(self, css, attribute_name):
        """
        Finds element by css. Returns specified attribute.
        :param css:
        :param attribute_name:
        """
        element = self.driver.find_element_by_css_selector(css)
        attribute = element.get_attribute(attribute_name)
        print attribute
        return attribute

    def get_attribute_by_id(self, element_id, attribute_name):
        """
        Finds element by id. Returns specified attribute.
        :param element_id:
        :param attribute_name:
        """
        element = self.driver.find_element_by_id(element_id)
        attribute = element.get_attribute(attribute_name)
        print attribute
        return attribute

    def get_attribute_by_xpath(self, xpath, attribute_name):
        """
        Finds element by xpath. Returns specified attribute.
        :param xpath:
        :param attribute_name:
        """
        element = self.driver.find_element_by_xpath(xpath)
        attribute = element.get_attribute(attribute_name)
        print attribute
        return attribute

    def scroll_to_element_by_id(self, element_id):
        """
        Finds the element and scrolls to it.
        :param element_id:
        """
        element = self.driver.find_element_by_id(element_id)
        self.driver.execute_script('arguments[0].scrollIntoView(true);', element)

    def scroll_to_element_by_css(self, css):
        """
        Finds the element and scrolls to it.
        :param css:
        """
        element = self.driver.find_element_by_css_selector(css)
        self.driver.execute_script('arguments[0].scrollIntoView(true);', element)

    def scroll_to_element_by_xpath(self, xpath):
        """
        Finds the element and scrolls to it.
        :param xpath:
        """
        element = self.driver.find_element_by_xpath(xpath)
        self.driver.execute_script('arguments[0].scrollIntoView(true);', element)
