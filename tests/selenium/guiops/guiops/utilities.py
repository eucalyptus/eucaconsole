from selenium import webdriver
from selenium import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import unittest, time, re




class UICheckException(Exception):
    def __init__(self, message):
        raise Exception(message)


class Utilities():

    def __init__(self,driver):
        """

        :param driver: webdriver
        """
        assert isinstance(driver, webdriver.Firefox)
        self.driver = driver



    retry = 400

    #def NoOp(self):
    #    return 0

   # def setSeleniumWebDriver(self, driver):
   #     self.driver = RemoteWebdriver()
   #     return 0
    def setUp(self):
        self.verificationErrors = []

    def is_element_present(self, how, what):
        try:
            self.driver.verify_element_present(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return True

    def wait_for_visible_by_id(self, element_id):
        is_visible = False
        for i in range(self.retry):
            is_visible = self.driver.find_element_by_id(element_id).is_displayed()
            if is_visible is True:
                print "Element " + element_id + " is visible"
                break
            time.sleep(1)

    def wait_for_visible_by_css_selector(self, css_selector):
        is_visible = False
        for i in range(self.retry):
            is_visible = self.driver.find_element_by_css_selector(css_selector).is_displayed()
            if is_visible is True:
                print "Element " + css_selector + " is visible"
                break
            time.sleep(1)

    def wait_for_visible_by_xpath(self, xpath):
        is_visible = False
        for i in range(self.retry):
            is_visible = self.driver.find_element_by_xpath(xpath).is_displayed()
            if is_visible is True:
                print "Element " + xpath + " is visible"
                break
            time.sleep(1)

    def wait_for_visible(self, element_type, element):
        """
        :param element_type:
        :param element:
        :return: :raise:
        """

        self.check_if_element_present_by_type(element_type, element)

        is_visible = False
        for i in range(self.retry):
            print "Wait On Visiblity:: Trial: " + str(i) + " Element Type: " + element_type + ", Element: " + element
            if element_type is "LINK_TEXT":
                is_visible = self.driver.find_element_by_link_text(element).is_displayed()
            elif element_type is "ID":
                is_visible = self.driver.find_element_by_id(element).is_displayed()
            elif element_type is "CSS_SELECTOR":
                is_visible = self.driver.find_element_by_css_selector(element).is_displayed()
            elif element_type is "XPATH":
                is_visible = self.driver.find_element_by_xpath(element).is_displayed()
            elif element_type is "NAME":
                is_visible = self.driver.find_element_by_name(element).is_displayed()

            if is_visible is True:
                print "Element " + element + " is visible"
                break
            time.sleep(1)

        if is_visible is False:
            print "Element " + element + " is NOT visible!"

        return is_visible


    def click_on_visible_by_id(self, element_id):
        self.wait_for_visible_by_id(element_id)
        self.click_element_by_id(element_id)

    def click_on_visible_by_css_selector(self,css_selector):
        self.wait_for_visible_by_css_selector(css_selector)
        self.click_element_by_css_selector(css_selector)




    def click_on_visible(self, element_type, element):
        self.wait_for_visible(element_type, element)
        if element_type is "LINK_TEXT":
            self.click_element_by_link_text(element)
        elif  element_type is "ID":
            self.click_element_by_id(element)
        elif element_type is "CSS_SELECTOR":
            self.click_element_by_css_selector(element)
        elif element_type is "XPATH":
            self.click_element_by_xpath(element)
        elif element_type is "NAME":
            self.click_element_by_name(element)




    def check_if_element_present_by_type(self, element_type, element):
        """
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
                if self.is_element_present(this_element_type, element):
                    break
            except:
                pass
            #raise UICheckException("Time out")
            time.sleep(1)
            # else:
            #     self.fail("timed out after "+`self.retry`+" seconds")

        try:
            self.is_element_present(this_element_type, element)
        except AssertionError as e:
            self.verificationErrors.append(str(e))
            print "TEST FAILED::: Wait On:: Element Type: " + element_type + ", Element: " + element
            raise UICheckException("Failed to find element of type " + element_type + element + " present")

        print "Found:: Element type: " + element_type + ", Element: " + element
        return 0

    def verify_visible_element_by_link_text(self, element):
        return self.driver.find_element_by_link_text(element).is_displayed()

    def verify_visible_element_by_id(self, element):
        return self.driver.find_element_by_id(element).is_displayed()

    def verify_visible_element_by_css_selector(self, element):
        return self.driver.find_element_by_css_selector(element).is_displayed()

    def verify_visible_element_by_xpath(self, element):
        return self.driver.find_element_by_xpath(element).is_displayed()

    def verify_visible_element_by_name(self, element):
        return self.driver.find_element_by_name(element).is_displayed()


    def verify_element_not_present(self, element_type, element):

        """
        Driver waits for the element to disappear from the page
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

    def verify_text_not_present_by_css(self, locator, text):
        print"Verifying that text displayed at " + locator + " does not match " + text
        for i in range(1, self.retry, 1):
            displayed = self.store_text_by_css_selector(locator)
            print "Currently displayed at locator " + locator + " is " + displayed
            if displayed != text:
                print "Verified " + self.store_text_by_css_selector(locator) + " does not match " + text
                return True
            else:
                print
                print "Trial " + str(i) + " :"

    def verify_text_not_present_by_id(self, locator, text):
        print"Verifying that text displayed at " + locator + " does not match " + text
        for i in range(1, self.retry, 1):
            if self.store_text_by_id(locator) != text:
                print "Verified " + self.store_text_by_id(locator) + " does not match " + text
                return True
            else:
                print
                print "Trial " + str(i) + " :"

    def verify_text_not_present_by_name(self, locator, text):
        print"Verifying that text displayed at " + locator + " does not match " + text
        for i in range(1, self.retry, 1):
            if self.store_text_by_name(locator) != text:
                print "Verified " + self.store_text_by_name(locator) + " does not match " + text
                return True
            else:
                print
                print "Trial " + str(i) + " :"

    def verify_text_not_present_by_xpath(self, locator, text):
        print"Verifying that text displayed at " + locator + " does not match " + text
        for i in range(1, self.retry, 1):
            text_on_page = self.store_text_by_xpath(locator)
            time.sleep(10)
            if text_on_page != text:
                print "Verified " + self.store_text_by_xpath(locator) + " does not match " + text
                return True
            else:
                print
                print "Found text: " + text_on_page + "( Waiting for " + text + " to disappear )"
                print
                print "Trial " + str(i) + " :"

    def verify_text_displayed_by_id(self, element_id, element_text):
        #print("Verifying text " +element_text+" displayed at ID "+element_id)
        for i in range(self.retry):
            print "Wait On:: Trial: " + str(i) + " Verifying text " + element_text + " displayed at ID " + element_id
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
        #print("Verifying text " +element_text+" displayed at ID "+element_css)
        for i in range(self.retry):
            print "Wait On:: Trial: " + str(i) + " Verifying text " + element_text + " displayed at ID " + element_css
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

    def verify_text_displayed_by_xpath(self, locator, element_text):
        #print("Verifying text " +element_text+" displayed at xpath "+locator)
        displayed_text = None
        for i in range(self.retry):
            print "Wait On:: Trial: " + str(i) + " Verifying text " + element_text + " displayed at xpath " + locator
            try:
                text_on_page = self.store_text_by_xpath(locator)
                if element_text == text_on_page:
                    print"Found text"
                    displayed_text = text_on_page
                    break
            except:
                pass
            time.sleep(1)
        try:
            text_on_page = self.store_text_by_xpath(locator)
            element_text == text_on_page
        except AssertionError as e:
            self.verificationErrors.append(str(e))

        print("Text displayed at xpath " + locator + " is " + displayed_text)

    def click_element_by_link_text(self, link_text):
        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present: " + link_text)
        if self.verify_visible_element_by_link_text( link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Click: Element Type: LINK_TEXT, Element: " + link_text
        self.driver.find_element_by_link_text(link_text).click()
        time.sleep(1)
        return 0

    def click_element_by_id(self, this_id):
        if self.check_if_element_present_by_type("ID", this_id) is not 0:
            raise UICheckException("Element by id not present: " + this_id)
        if self.verify_visible_element_by_id(this_id) is not True:
            raise UICheckException("Element by id not visible:" + this_id)
        print "Click: Element Type: ID, Element: " + this_id
        self.driver.find_element_by_id(this_id).click()
        time.sleep(1)
        return 0

    def click_element_by_css_selector(self, css_selector):
        if self.check_if_element_present_by_type("CSS_SELECTOR", css_selector) is not 0:
            raise UICheckException("Element by css selector not present: " + css_selector)
        if self.verify_visible_element_by_css_selector( css_selector) is not True:
            raise UICheckException("Element by css selector not visible:" + css_selector)
        print "Click: Element Type: CSS_SELECTOR, Element: " + css_selector
        self.driver.find_element_by_css_selector(css_selector).click()
        time.sleep(1)
        return 0

    def click_element_by_xpath(self, xpath):
        if self.check_if_element_present_by_type("XPATH", xpath) is not 0:
            raise UICheckException("Element by xpath not present: " + xpath)
#        if self.check_if_element_visible_by_type("XPATH", xpath) is not True:
#            raise UICheckException("Element by xpath not visible:" + xpath)
        print "Click: Element Type: XPATH, Element: " + xpath
        self.driver.find_element_by_xpath(xpath).click()
        time.sleep(1)
        return 0

    def click_element_by_name(self, name):
        if self.check_if_element_present_by_type("NAME", name) is not 0:
            raise UICheckException("Element by name not present: " + name)
        if self.verify_text_not_present_by_name("NAME", name) is not True:
            raise UICheckException("Element by name not visible:" + name)
        print "Click: Element Type: NAME, Element: " + name
        self.driver.find_element_by_name(name).click()
        return 0

    def send_keys_by_link_text(self, link_text, keys):
        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present:" + link_text)
        if self.verify_visible_element_by_link_text(link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Set: Element Type: LINK_TEXT, Element: " + link_text + ", Keys: " + keys
        self.driver.find_element_by_link_text(link_text).clear()
        self.driver.find_element_by_link_text(link_text).send_keys(keys)
        return 0

    def send_keys_by_id(self, this_id, keys):
        if self.check_if_element_present_by_type("ID", this_id) is not 0:
            raise UICheckException("Element by id not present:" + this_id)
        if self.verify_visible_element_by_id( this_id) is not True:
            raise UICheckException("Element by id not visible:" + this_id)
        print "Set: Element Type: ID, Element: " + this_id + ", Keys: " + keys
        self.driver.find_element_by_id(this_id).clear()
        self.driver.find_element_by_id(this_id).send_keys(keys)
        return 0

    def send_keys_by_css_selector(self, css_selector, keys):
        if self.check_if_element_present_by_type("CSS_SELECTOR", css_selector) is not 0:
            raise UICheckException("Element by css selector not present:" + css_selector)
        if self.verify_visible_element_by_css_selector( css_selector) is not True:
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
        if self.verify_visible_element_by_name( name) is not True:
            raise UICheckException("Element by name not visible:" + name)
        print "Set: Element Type: NAME, Element: " + name + ", Keys: " + keys
        self.driver.find_element_by_name(name).clear()
        return 0

    def store_text_by_link_text(self, link_text):
        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present:" + link_text)
        if self.verify_visible_element_by_link_text(link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Get Text: Element Type: LINK_TEXT, Element: " + link_text
        return self.driver.find_element_by_link_text(link_text).text

    def store_text_by_id(self, this_id):
        if self.check_if_element_present_by_type("ID", this_id) is not 0:
            raise UICheckException("Element by id not present:" + this_id)
        if self.verify_visible_element_by_id(this_id) is not True:
            raise UICheckException("Element by id not visible:" + this_id)
        print "Get Text: Element Type: ID, Element: " + this_id
        return self.driver.find_element_by_id(this_id).text

    def store_text_by_css_selector(self, css_selector):
        if self.check_if_element_present_by_type("CSS_SELECTOR", css_selector) is not 0:
            raise UICheckException("Element by css selector not present:" + css_selector)
        if self.verify_visible_element_by_css_selector(css_selector) is not True:
            raise UICheckException("Element by css selector not visible:" + css_selector)
        print "Get Text: Element Type: CSS_SELECTOR, Element: " + css_selector
        return self.driver.find_element_by_css_selector(css_selector).text

    def store_text_by_xpath(self, xpath):
        if self.check_if_element_present_by_type("XPATH", xpath) is not 0:
            raise UICheckException("Element by xpath not present: " + xpath)
#        if self.check_if_element_visible_by_type("XPATH", xpath) is not True:
#            raise UICheckException("Element by xpath not visible:" + xpath)
        print "Get Text: Element Type: XPATH, Element: " + xpath
        return self.driver.find_element_by_xpath(xpath).text

    def store_text_by_name(self, name):
        if self.check_if_element_present_by_type("NAME", name) is not 0:
            raise UICheckException("Element by name not present: " + name)
        if self.verify_visible_element_by_name( name) is not True:
            raise UICheckException("Element by name not visible:" + name)
        print "Click: Element Type: NAME, Element: " + name
        return self.driver.find_element_by_name(name).text

    def select_text_by_link_text(self, link_text, visible_text):
        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present: " + link_text)
        if self.verify_visible_element_by_link_text(link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Select: Element Type: LINK_TEXT, Element: " + link_text + ", Text: " + visible_text
        Select(self.driver.find_element_by_link_text(link_text)).select_by_visible_text(visible_text)
        return 0

    def select_text_by_id(self, this_id, visible_text):
        if self.check_if_element_present_by_type("ID", this_id) is not 0:
            raise UICheckException("Element by id not present: " + this_id)
        if self.verify_visible_element_by_id(this_id) is not True:
            raise UICheckException("Element by id not visible:" + this_id)
        print "Select: Element Type: ID, Element: " + this_id + ", Text: " + visible_text
        Select(self.driver.find_element_by_id(this_id)).select_by_visible_text(visible_text)
        return 0

    def select_text_by_css_selector(self, css_selector, visible_text):
        if self.check_if_element_present_by_type("CSS_SELECTOR", css_selector) is not 0:
            raise UICheckException("Element by css selector not present: " + css_selector)
        if self.verify_visible_element_by_css_selector(css_selector) is not True:
            raise UICheckException("Element by css selector not visible:" + css_selector)
        print "Select: Element Type: CSS_SELECTOR, Element: " + css_selector + ", Text: " + visible_text
        Select(self.driver.find_element_by_css_selector(css_selector)).select_by_visible_text(visible_text)
        return 0

    def select_text_by_xpath(self, xpath, visible_text):
        if self.check_if_element_present_by_type("XPATH", xpath) is not 0:
            raise UICheckException("Element by xpath not present: " + xpath)
#        if self.check_if_element_visible_by_type("XPATH", xpath) is not True:
#            raise UICheckException("Element by xpath not visible:" + xpath)
        print "Select: Element Type: XPATH, Element: " + xpath + ", Text: " + visible_text
        Select(self.driver.find_element_by_xpath(xpath)).select_by_visible_text(visible_text)
        return 0

    def select_text_by_name(self, name, visible_text):
        if self.check_if_element_present_by_type("NAME", name) is not 0:
            raise UICheckException("Element by name not present: " + name)
        if self.verify_visible_element_by_name(name) is not True:
            raise UICheckException("Element by name not visible:" + name)
        print "Select: Element Type: NAME, Element: " + name + ", Text: " + visible_text
        Select(self.driver.find_element_by_name(name)).select_by_visible_text(visible_text)
        return 0

