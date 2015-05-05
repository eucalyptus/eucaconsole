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


class SeleniumApi():
    def __init__(self, driver):
        """

        :param driver: webdriver
        """
        assert isinstance(driver, webdriver.Firefox)
        self.driver = driver


    retry = 2
    timeout_to_locate_element_in_seconds = 60
    timeout_to_determine_visibility_in_seconds = 60
    timeout_to_determine_if_clickable_in_seconds = 20

    #def NoOp(self):
    #    return 0

    # def setSeleniumWebDriver(self, driver):
    #     self.driver = RemoteWebdriver()
    #     return 0
    #def setUp(self):
    #    self.verificationErrors = []

    def set_implicit_wait(self, implicit_wait_time):
        """
        Sets implicit wait for webdriver
        :param implicit_wait_time:
        """
        self.driver.implicitly_wait(self, implicit_wait_time)

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

    def wait_for_element_present_by_css(self, css):
        """
        Waits for element to be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        """
        print "Executing wait_for_element_present_by_css ('{0}')".format(css)
        print "Looking for element by css = '{0}' in the DOM.".format(css)
        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, css)))
            print "Found element by css = '{0}'".format(css)
        except NoSuchElementException, nse:
            print "Did not find element by css = '{0}'".format(css)
        except TimeoutException, t:
            print "ERROR: Timed out. Did not find element by css = '{0}'".format(css)

    def wait_for_visible_by_id(self, element_id):
        """
        Waits for the element to become visible. First, checks if element is present.
        :param element_id:
        """

        print "Executing wait_for_visible_by_id('{0}')".format(element_id)

        try:
            self.wait_for_element_present_by_id(element_id)
            WebDriverWait(self.driver, self.timeout_to_determine_visibility_in_seconds).until(EC.visibility_of_element_located((By.ID,element_id)))
            print "Element by id = '{0}' was located in DOM and is visible.".format(element_id)
        except TimeoutException:
            print "ERROR: Timed out: element by id = '{0}' not visible.".format(element_id)

    def wait_for_visible_by_css(self, css):
        """
        Waits for the element to become visible. First, checks if element is present.
        :param css:
        """

        print "Executing wait_for_visible_by_css('{0}')".format(css)

        try:
            self.wait_for_element_present_by_css(css)
            WebDriverWait(self.driver, self.timeout_to_determine_visibility_in_seconds).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
            print "Element by icss = '{0}' was located in DOM and is visible.".format(css)
        except TimeoutException:
            print "ERROR: Timed out: element by css = '{0}' not visible.".format(css)

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

    def click_element_by_id(self, element_id):
        """
        Waits for an element to be present, visible and enabled such that you can click it.
        Clicks the element.
        :param element_id:
        """
        print "Executing click_element_by_id('{0}')".format(element_id)

        self.wait_for_clickable_by_id(element_id)
        try:
            self.driver.find_element_by_id(element_id).click()
            print "Clicking on element by id = ('{0}')".format(element_id)
        except Exception, e:
            print "ERROR: Could not perform click on element by id = ('{0}')".format(element_id)

    def click_element_by_css(self, css):
        """
        Waits for an element to be present, visible and enabled such that you can click it.
        Clicks the element.
        :param css:
        """
        print "Executing click_element_by_css('{0}')".format(css)

        self.wait_for_clickable_by_css(css)
        try:
            self.driver.find_element_by_css_selector(css).click()
            print "Clicking on element by css = ('{0}')".format(css)
        except Exception, e:
            print "ERROR: Could not perform click on element by css = ('{0}')".format(css)

    def wait_for_element_not_present_by_id(self, element_id):
        """
        Waits for element to NOT be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        """
        print "Executing wait_for_element_not_present_by_id('{0}')".format(element_id)
        print "Looking for element id = '{0}' in the DOM".format(element_id)
        try:
            WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until_not(
                EC.presence_of_element_located((By.ID, element_id)))
            print "Verified element by id = '{0}' not in the DOM".format(element_id)
        except Exception, e:
            print "ERROR: Can not verify the element by id = '{0}' is not in the DOM".format(element_id)
        except TimeoutException, t:
            print "ERROR: Timed out. Element by id = '{0}' still found in the DOM.".format(element_id)

############################################################################################################################
    def verify_element_not_present(self, element_type, element):

        """
        Waits for the element to disappear from the page.
        Keeps checking until max number or retries self.retry is reached.
        :param element_type:
        :param element:
        """

        this_element_type = ""
        if element_type is "LINK_TEXT":
            this_element_type = By.LINK_TEXT
        elif element_type is "ID":
            this_element_type = By.ID
        elif element_type is "CSS_SELECTOR":
            this_element_type = By.CSS_SELECTOR
        elif element_type is "XPATH":
            this_element_type = By.XPATH
        elif element_type is "NAME":
            this_element_type = By.NAME

        for i in range(1, self.retry, 1):
            print "Wait On Removal:: Trial: " + str(i) + " Element Type: " + element_type + ", Element: " + element
            try:
                self.driver.verify_element_present(this_element_type, element)
            except NoSuchElementException:
                print
                print "Verified Removal:: Element type: " + element_type + ", Element: " + element
                return True
            time.sleep(1)
        return False

    def verify_text_not_present_by_css(self, css, text):
        """
        Waits for the element to disappear from the page by css.
        Keeps checking until max number or retries self.retry is reached.
        :param css:
        :param text:
        """
        print"Verifying that text displayed at " + css + " does not match " + text
        for i in range(1, self.retry, 1):
            displayed = self.store_visible_text_by_css_selector(css)
            print "Currently displayed at locator " + css + " is " + displayed
            if displayed != text:
                print "Verified " + self.store_visible_text_by_css_selector(css) + " does not match " + text
                return True
            else:
                print
                print "Trial " + str(i) + " :"

    def verify_text_not_present_by_id(self, element_id, text):
        """
        Waits for the element to disappear from the page by id.
        Keeps checking until max number or retries self.retry is reached.
        :param element_id:
        :param text:
        """
        print"Verifying that text displayed at " + element_id + " does not match " + text
        for i in range(1, self.retry, 1):
            if self.store_visible_text_by_id(element_id) != text:
                print "Verified " + self.store_visible_text_by_id(element_id) + " does not match " + text
                return True
            else:
                print
                print "Trial " + str(i) + " :"

    def verify_text_not_present_by_name(self, name, text):
        """
        Waits for the element to disappear from the page by name.
        Keeps checking until max number or retries self.retry is reached.
        """
        print"Verifying that text displayed at " + name + " does not match " + text
        for i in range(1, self.retry, 1):
            if self.store_visible_text_by_name(name) != text:
                print "Verified " + self.store_visible_text_by_name(name) + " does not match " + text
                return True
            else:
                print
                print "Trial " + str(i) + " :"

    def verify_text_not_present_by_xpath(self, xpath, text):
        """
        Waits for the element to disappear from the page by xpath.
        Keeps checking until max number or retries self.retry is reached.
        :param xpath:
        :param text:
        """
        print"Verifying that text displayed at " + xpath + " does not match " + text
        for i in range(1, self.retry, 1):
            text_on_page = self.store_visible_text_by_xpath(xpath)
            time.sleep(10)
            if text_on_page != text:
                print "Verified " + self.store_visible_text_by_xpath(xpath) + " does not match " + text
                return True
            else:
                print
                print "Found text: " + text_on_page + "( Waiting for " + text + " to disappear )"
                print
                print "Trial " + str(i) + " :"

    def verify_text_displayed_by_id(self, element_id, element_text):
        """
        Will wait for element to become visible. Will check if text displayed at element_id matches element_text.
        Keeps checking until max number or retries self.retry is reached.

        :param element_id:
        :param element_text:
        """
        #print("Verifying text " +element_text+" displayed at ID "+element_id)
        for i in range(self.retry):
            print "Wait On:: Trial: " + str(i) + " Verifying text " + element_text + " displayed at ID " + element_id
            self.wait_for_visible_by_id(element_id)
            try:
                if element_text == self.driver.find_element_by_id(element_id).text:
                    print"Found text"
                    displayed_text = self.driver.find_element_by_id(element_id).text
                    print("Text displayed at ID " + element_id + " is " + displayed_text)
                    break
            except:
                pass

            time.sleep(1)

    def verify_text_displayed_by_css(self, element_css, element_text):
        """
        Will wait for element to become visible. Will check if text displayed at element_css matches element_text.
        Keeps checking until max number or retries self.retry is reached.
        :param element_css:
        :param element_text:
        """
        #print("Verifying text " +element_text+" displayed at ID "+element_css)
        for i in range(self.retry):
            print "Wait On:: Trial: " + str(i) + " Verifying text " + element_text + " displayed at ID " + element_css
            self.wait_for_visible_by_css_selector(element_css)
            try:
                if element_text == self.driver.find_element_by_css_selector(element_css).text:
                    print"Found text"
                    break
            except:
                pass
            time.sleep(1)
        try:
            self.driver.find_element_by_css_selector(element_css).text
        except AssertionError as e:
            self.verificationErrors.append(str(e))

        displayed_text = self.driver.find_element_by_css_selector(element_css).text
        print("Text displayed at ID " + element_css + " is " + displayed_text)

    def verify_text_displayed_by_xpath(self, xpath, element_text):
        """
        Will wait for element to become visible. Will check if text displayed at xpath matches element_text.
        Keeps checking until max number or retries self.retry is reached.
        :param xpath:
        :param element_text:
        """
        #print("Verifying text " +element_text+" displayed at xpath "+locator)
        displayed_text = None
        for i in range(self.retry):
            print "Wait On:: Trial: " + str(i) + " Verifying text " + element_text + " displayed at xpath " + xpath
            self.wait_for_visible_by_xpath(xpath)
            try:
                text_on_page = self.store_visible_text_by_xpath(xpath)
                if element_text == text_on_page:
                    print"Found text"
                    displayed_text = text_on_page
                    break
            except:
                pass
            time.sleep(1)
        try:
            text_on_page = self.store_visible_text_by_xpath(xpath)
            if element_text == text_on_page:
                print "Found text"
                displayed_text = text_on_page
        except AssertionError as e:
            self.verificationErrors.append(str(e))

        print("Text displayed at xpath " + xpath + " is " + displayed_text)

    def send_keys_by_link_text(self, link_text, keys):
        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present:" + link_text)
        if self.verify_element_visible_by_link_text(link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Set: Element Type: LINK_TEXT, Element: " + link_text + ", Keys: " + keys
        self.driver.find_element_by_link_text(link_text).clear()
        self.driver.find_element_by_link_text(link_text).send_keys(keys)
        return 0

    def send_keys_by_id(self, this_id, keys):
        if self.check_if_element_present_by_type("ID", this_id) is not 0:
            raise UICheckException("Element by id not present:" + this_id)
        if self.verify_element_visible_by_id(this_id) is not True:
            raise UICheckException("Element by id not visible:" + this_id)
        print "Set: Element Type: ID, Element: " + this_id + ", Keys: " + keys
        self.driver.find_element_by_id(this_id).clear()
        self.driver.find_element_by_id(this_id).send_keys(keys)
        return 0

    def send_keys_by_css_selector(self, css_selector, keys):
        if self.check_if_element_present_by_type("CSS_SELECTOR", css_selector) is not 0:
            raise UICheckException("Element by css selector not present:" + css_selector)
        if self.verify_element_visible_by_css_selector(css_selector) is not True:
            raise UICheckException("Element by css selector not visible:" + css_selector)
        print "Set: Element Type: CSS_SELECTOR, Element: " + css_selector + ", Keys: " + keys
        self.driver.find_element_by_css_selector(css_selector).clear()
        self.driver.find_element_by_css_selector(css_selector).send_keys(keys)
        return 0

    def send_keys_by_xpath(self, xpath, keys):
        if self.check_if_element_present_by_type("XPATH", xpath) is not 0:
            raise UICheckException("Element by xpath not found :" + xpath)
            #        if self.check_if_element_visible_by_type("XPATH", xpath) is not True:
        #            raise UICheckException("Element by xpath not visible:" + xpath)
        print "Set: Element Type: XPATH, Element: " + xpath + ", Keys: " + keys
        self.driver.find_element_by_xpath(xpath).clear()
        self.driver.find_element_by_xpath(xpath).send_keys(keys)
        return 0

    def send_keys_by_name(self, name, keys):
        if self.check_if_element_present_by_type("NAME", name) is not 0:
            raise UICheckException("Element by name not found:" + name)
        if self.verify_element_visible_by_name(name) is not True:
            raise UICheckException("Element by name not visible:" + name)
        print "Set: Element Type: NAME, Element: " + name + ", Keys: " + keys
        self.driver.find_element_by_name(name).clear()
        return 0

    def store_visible_text_by_link_text(self, link_text):
        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present:" + link_text)
        if self.verify_element_visible_by_link_text(link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Get Text: Element Type: LINK_TEXT, Element: " + link_text
        return self.driver.find_element_by_link_text(link_text).text

    def store_visible_text_by_id(self, this_id):
        if self.check_if_element_present_by_type("ID", this_id) is not 0:
            raise UICheckException("Element by id not present:" + this_id)
        if self.verify_element_visible_by_id(this_id) is not True:
            raise UICheckException("Element by id not visible:" + this_id)
        print "Get Text: Element Type: ID, Element: " + this_id
        return self.driver.find_element_by_id(this_id).text

    def store_visible_text_by_css_selector(self, css_selector):
        if self.check_if_element_present_by_type("CSS_SELECTOR", css_selector) is not 0:
            raise UICheckException("Element by css selector not present:" + css_selector)
        if self.verify_element_visible_by_css_selector(css_selector) is not True:
            raise UICheckException("Element by css selector not visible:" + css_selector)
        print "Get Text: Element Type: CSS_SELECTOR, Element: " + css_selector
        return self.driver.find_element_by_css_selector(css_selector).text

    def store_visible_text_by_xpath(self, xpath):
        if self.check_if_element_present_by_type("XPATH", xpath) is not 0:
            raise UICheckException("Element by xpath not present: " + xpath)
            #        if self.check_if_element_visible_by_type("XPATH", xpath) is not True:
        #            raise UICheckException("Element by xpath not visible:" + xpath)
        print "Get Text: Element Type: XPATH, Element: " + xpath
        return self.driver.find_element_by_xpath(xpath).text

    def store_visible_text_by_name(self, name):
        if self.check_if_element_present_by_type("NAME", name) is not 0:
            raise UICheckException("Element by name not present: " + name)
        if self.verify_element_visible_by_name(name) is not True:
            raise UICheckException("Element by name not visible:" + name)
        print "Click: Element Type: NAME, Element: " + name
        return self.driver.find_element_by_name(name).text

    def select_visible_text_by_link_text(self, link_text, visible_text):
        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present: " + link_text)
        if self.verify_element_visible_by_link_text(link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Select: Element Type: LINK_TEXT, Element: " + link_text + ", Text: " + visible_text
        Select(self.driver.find_element_by_link_text(link_text)).select_by_visible_text(visible_text)
        return 0

    def select_visible_text_by_id(self, this_id, visible_text):
        if self.check_if_element_present_by_type("ID", this_id) is not 0:
            raise UICheckException("Element by id not present: " + this_id)
        if self.verify_element_visible_by_id(this_id) is not True:
            raise UICheckException("Element by id not visible:" + this_id)
        print "Select: Element Type: ID, Element: " + this_id + ", Text: " + visible_text
        Select(self.driver.find_element_by_id(this_id)).select_by_visible_text(visible_text)
        return 0

    def select_visible_text_by_css_selector(self, css_selector, visible_text):
        if self.check_if_element_present_by_type("CSS_SELECTOR", css_selector) is not 0:
            raise UICheckException("Element by css selector not present: " + css_selector)
        if self.verify_element_visible_by_css_selector(css_selector) is not True:
            raise UICheckException("Element by css selector not visible:" + css_selector)
        print "Select: Element Type: CSS_SELECTOR, Element: " + css_selector + ", Text: " + visible_text
        Select(self.driver.find_element_by_css_selector(css_selector)).select_by_visible_text(visible_text)
        return 0

    def select_visible_text_by_xpath(self, xpath, visible_text):
        if self.check_if_element_present_by_type("XPATH", xpath) is not 0:
            raise UICheckException("Element by xpath not present: " + xpath)
            #        if self.check_if_element_visible_by_type("XPATH", xpath) is not True:
        #            raise UICheckException("Element by xpath not visible:" + xpath)
        print "Select: Element Type: XPATH, Element: " + xpath + ", Text: " + visible_text
        Select(self.driver.find_element_by_xpath(xpath)).select_by_visible_text(visible_text)
        return 0

    def select_visible_text_by_name(self, name, visible_text):
        if self.check_if_element_present_by_type("NAME", name) is not 0:
            raise UICheckException("Element by name not present: " + name)
        if self.verify_element_visible_by_name(name) is not True:
            raise UICheckException("Element by name not visible:" + name)
        print "Select: Element Type: NAME, Element: " + name + ", Text: " + visible_text
        Select(self.driver.find_element_by_name(name)).select_by_visible_text(visible_text)
        return 0

    def check_if_element_present_by_type(self, element_type, element):
        """
        Checks if element is present using element type and its locator.
        Keeps checking until max number of trials self.retry are exhausted.
        :param element_type:
        :param element:
        :return: :raise:
        """
        this_element_type = ""
        if element_type is "LINK_TEXT":
            this_element_type = By.LINK_TEXT
        elif element_type is "ID":
            this_element_type = By.ID
        elif element_type is "CSS_SELECTOR":
            this_element_type = By.CSS_SELECTOR
        elif element_type is "XPATH":
            this_element_type = By.XPATH
        elif element_type is "NAME":
            this_element_type = By.NAME

        for i in range(self.retry):
            print "Wait On:: Trial: " + str(i) + " Element Type: " + element_type + ", Element: " + element
            try:
                if self.verify_element_present(this_element_type, element):
                    break
            except:
                pass
                #raise UICheckException("Time out")
            time.sleep(1)
            # else:
            #     self.fail("timed out after "+`self.retry`+" seconds")

        try:
            self.verify_element_present(this_element_type, element)
        except AssertionError as e:
            self.verificationErrors.append(str(e))
            print "TEST FAILED::: Wait On:: Element Type: " + element_type + ", Element: " + element
            raise UICheckException("Failed to find element of type " + element_type + element + " present")

        print "Found:: Element type: " + element_type + ", Element: " + element
        return 0