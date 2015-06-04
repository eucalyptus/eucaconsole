from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import time


class UICheckException(Exception):
    def __init__(self, message):
        raise Exception(message)


class SeleniumApi_experimental():
    def __init__(self, driver):
        """

        :param driver: webdriver
        """
        assert isinstance(driver, webdriver.Firefox)
        self.driver = driver


    retry = 400
    timeout_to_locate_element_in_seconds = 30
    timeout_to_determine_visibility_in_seconds = 5
    timeout_to_determine_if_clickable_in_seconds = 20

    def wait_for_element_present_by_id_experimental(self, element_id):
        """
        Waits for element to be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        """
        print "Executing wait_for_element_present_by_id("+element_id+")"
        print "Looking for element id = " + element_id + " in the DOM."
        print "Timeout is set to " + str(self.timeout_to_locate_element_in_seconds) + " seconds"

       # element_present = self.driver.find_element(By.ID, element_id)

        wait = WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds, 1, (NoSuchElementException))
        def my_method():
            try:
                self.driver.find_element(By.ID, element_id)
                return True
            except NoSuchElementException, nse:
                return False
        wait.until(my_method, message="Found element")

        return 0


    def wait_for_element_present_by_id_experimental(self, element_id):
        """
        Waits for element to be present on the page for timeout_to_locate_element_in_seconds
        Checks for presence every 500 milliseconds
        """
        print "Executing wait_for_element_present_by_id("+element_id+")"
        print "Looking for element id = " + element_id + " in the DOM."
        print "Timeout is set to " + str(self.timeout_to_locate_element_in_seconds) + " seconds"

       # element_present = self.driver.find_element(By.ID, element_id)

        #wait = WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds, 1, (NoSuchElementException))
        def my_method(self):
            try:
                self.driver.find_element_by_id(element_id)
                return True
            except NoSuchElementException, nse:
                return False
        WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(my_method, "Found element")

        return 0


    def wait_for_element_not_present_by_id_experimental(self, element_id):

        print "Executing wait_for_element_not_present_by_id("+element_id+")"
        print "Looking for element id = " + element_id + " in the DOM."
        print "Timeout is set to " + str(self.timeout_to_locate_element_in_seconds) + " seconds"

        wait = WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds)

        if wait.until_not(EC.presence_of_element_located((By.ID, element_id))):

            print "Verified element id = " + element_id + " not present."

        else:
            raise UICheckException
        return 0

    def wait_for_visible_by_id_experimental(self, element_id):
        """
        Waits for element to become visible for timeout_to_determine_visibility_in_seconds
        Checks for presence and visibility every 500 milliseconds
        :param element_id:
        """
        print "Waiting for element id = " + element_id + " to become visible."

        if self.wait_for_element_present_by_id(element_id):

            wait = WebDriverWait(self.driver, self.timeout_to_determine_visibility_in_seconds)


            element = wait.until(EC.visibility_of_element_located((By.ID, element_id)))

# def verify_element_present_by_id(self, element_id):
    #
    #    """
    #    Tries to locate element by polling every 500ms until timeout_to_locate_element_in_seconds is reached.
    #    :param element_id:
    #    """
    #    element = WebDriverWait(self.driver, self.timeout_to_locate_element_in_seconds).until(
    #         EC.presence_of_element_located((By.ID, element_id)))
    #    print element

    def verify_element_visible_by_id_experimental(self, element_id):
        """
        Checks for visibility of element by polling every 500ms until
        timeout_to_determine_visibility_in_seconds is reached.
        :param element_id:
        """


        element = WebDriverWait(self.driver, self.timeout_to_determine_visibility_in_seconds).until(
            EC.visibility_of_element_located((By.ID, element_id))
        )
        print element
       # self.verify_element_present("ID", element_id)
       # self.set_implicit_wait(self.timeout_to_determine_visibility_in_seconds)
       # is_visible = False
       # try:
       #     is_visible = self.driver.find_element_by_id(element_id).is_displayed()

        #except ElementNotVisibleException:

        #    pass

        #finally:

        #    if is_visible:
        #        print "Element " + element_id + " is visible"

         #   else:
         #       print "Element " + element_id + " is not visible"



    def verify_element_clickable_by_id_experimental(self,element_id):
        """
        Checks whether the element is clickable by polling every 500ms until
        timeout_to_determine_if_clickable_in_seconds is reached.
        :param element_id:
        """
        element = WebDriverWait(self.driver, self.timeout_to_determine_if_clickable_in_seconds).until(
            EC.element_to_be_clickable((By.ID,element_id))
        )
        print element

#################################################

    def wait_for_visible(self, element_type, element):
        """
        Checks visibility of an element.
        Keeps checking for visibility until max number of trials self.retry is reached.
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
            print "Element " + element + " is not visible!"

        return is_visible

    def click_on_visible(self, element_type, element):
        """
        Waits for an element to become visible then clicks the element by its locator.
        :rtype : object
        :param element_type:
        :param element:
        """
        self.wait_for_visible(element_type, element)
        if element_type is "LINK_TEXT":
            self.click_element_by_link_text(element)
        elif element_type is "ID":
            self.click_element_by_id(element)
        elif element_type is "CSS_SELECTOR":
            self.click_element_by_css_selector(element)
        elif element_type is "XPATH":
            self.click_element_by_xpath(element)
        elif element_type is "NAME":
            self.click_element_by_name(element)

    def verify_element_present(self, how, what):
        """
        Finds element by locator. Takes as arguments element type and element locator.
        Will try locating element until implicit wait limit timeout_to_locate_element_in_seconds is reached.
        Returns NoSuchElementException if element is not found.
        :param how:
        :param what:
        """
        print "Executing verify_element_present (" + str(how) + " , " + str(what) + " )"

        self.set_implicit_wait(self.timeout_to_locate_element_in_seconds)
        try:
            self.driver.find_element(by=how, value=what)

        except NoSuchElementException:
            return False
        return True

    def verify_element_present(self, how, what):
        """
        Finds element by locator. Takes as arguments element type and element locator.
        Will try locating element until implicit wait limit timeout_to_locate_element_in_seconds is reached.
        Returns NoSuchElementException if element is not found.
        :param how:
        :param what:
        """
        print "Executing verify_element_present (" + str(how) + " , " + str(what) + " )"

        self.set_implicit_wait(self.timeout_to_locate_element_in_seconds)
        try:
            self.driver.find_element(by=how, value=what)

        except NoSuchElementException:
            return False
        return True

    def wait_for_visible_by_id(self, element_id):
        """
        Checks visibility of an element using its id.
        Keeps checking for visibility until max number of trials self.retry is reached.
        :param element_id:
        """

        print "Executing wait_for_visible_by_id( "+element_id+" )"

        self.wait_for_element_present_by_id(element_id)
        is_visible = False
        for i in range(self.retry):
            is_visible = self.driver.find_element_by_id(element_id).is_displayed()
            if is_visible is True:
                print "Element " + element_id + " is visible"
                break
            time.sleep(1)
        if is_visible is False:
            print "Element " + element_id + " is not visible"

    def wait_for_visible_by_css_selector(self, css):
        """
        Checks visibility of an element using its css.
        Keeps checking for visibility until max number of trials self.retry is reached.
        :param self:
        :param css:
        """
        is_visible = False
        for i in range(self.retry):
            is_visible = self.driver.find_element_by_css_selector(css).is_displayed()
            if is_visible is True:
                print "Element " + css + " is visible"
                break
            time.sleep(1)
        if is_visible is False:
            print "Element " + css + " is not visible"

    def wait_for_visible_by_xpath(self, xpath):
        """
        Checks visibility of an element using its xpath.
        Keeps checking for visibility until max number of trials self.retry is reached.
        :param xpath:
        """
        is_visible = False
        for i in range(self.retry):
            is_visible = self.driver.find_element_by_xpath(xpath).is_displayed()
            if is_visible is True:
                print "Element " + xpath + " is visible"
                break
            time.sleep(1)
        if is_visible is False:
            print "Element " + xpath + " is not visible"


    def click_element_by_link_text(self, link_text):

        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present: " + link_text)
        if self.verify_element_visible_by_link_text(link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Click: Element Type: LINK_TEXT, Element: " + link_text
        self.driver.find_element_by_link_text(link_text).click()
        time.sleep(1)
        return 0


    def click_element_by_css_selector(self, css_selector):
        if self.check_if_element_present_by_type("CSS_SELECTOR", css_selector) is not 0:
            raise UICheckException("Element by css selector not present: " + css_selector)
        if self.verify_element_visible_by_css_selector(css_selector) is not True:
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

    def click_on_visible_by_id(self, element_id):
        """
        Waits for an element to become visible then clicks the element by its id.
        :param element_id:
        """
        self.wait_for_visible_by_id(element_id)
        self.click_element_by_id(element_id)

    def click_on_visible_by_css_selector(self, css):
        """
        Waits for an element to become visible then clicks the element by its css.
        :param css:
        """
        self.wait_for_visible_by_css_selector(css)
        self.click_element_by_css_selector(css)



    def verify_element_visible_by_link_text(self, link_text):
        """
        Checks if element is visible using link text. Does not retry.
        :param link_text:
        """
        return self.driver.find_element_by_link_text(link_text).is_displayed()

    def verify_element_visible_by_id(self, element_id):
        """
        Checks if element is visible using id. Does not retry.
        :param element_id:
        """
        return self.driver.find_element_by_id(element_id).is_displayed()

    def verify_element_visible_by_css_selector(self, css):
        """
        Checks if element is visible using css. Does not retry.
        :param css:
        """
        return self.driver.find_element_by_css_selector(css).is_displayed()

    def verify_element_visible_by_xpath(self, xpath):
        """
        Checks if element is visible using xpath. Does not retry.
        :param xpath:
        """
        return self.driver.find_element_by_xpath(xpath).is_displayed()

    def verify_element_visible_by_name(self, name):
        """
        Checks if element is visible using name. Does not retry.
        :param name:
        """
        return self.driver.find_element_by_name(name).is_displayed()

    def send_keys_by_link_text(self, link_text, keys):
        if self.check_if_element_present_by_type("LINK_TEXT", link_text) is not 0:
            raise UICheckException("Element by link text not present:" + link_text)
        if self.verify_element_visible_by_link_text(link_text) is not True:
            raise UICheckException("Element by link text not visible:" + link_text)
        print "Set: Element Type: LINK_TEXT, Element: " + link_text + ", Keys: " + keys
        self.driver.find_element_by_link_text(link_text).clear()
        self.driver.find_element_by_link_text(link_text).send_keys(keys)
        return 0

    def select_visible_text_by_name(self, name, visible_text):
        if self.check_if_element_present_by_type("NAME", name) is not 0:
            raise UICheckException("Element by name not present: " + name)
        if self.verify_element_visible_by_name(name) is not True:
            raise UICheckException("Element by name not visible:" + name)
        print "Select: Element Type: NAME, Element: " + name + ", Text: " + visible_text
        Select(self.driver.find_element_by_name(name)).select_by_visible_text(visible_text)
        return 0

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
                self.driver.find_element(this_element_type, element)
            except NoSuchElementException:
                print
                print "Verified Removal:: Element type: " + element_type + ", Element: " + element
                return True

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
                if self.driver.find_element(this_element_type, element):
                    break
            except:
                pass
                #raise UICheckException("Time out")
            time.sleep(1)
            # else:
            #     self.fail("timed out after "+`self.retry`+" seconds")

        try:
            self.driver.find_element(this_element_type, element)
        except AssertionError as e:
            self.verificationErrors.append(str(e))
            print "TEST FAILED::: Wait On:: Element Type: " + element_type + ", Element: " + element
            raise UICheckException("Failed to find element of type " + element_type + element + " present")

        print "Found:: Element type: " + element_type + ", Element: " + element
        return 0