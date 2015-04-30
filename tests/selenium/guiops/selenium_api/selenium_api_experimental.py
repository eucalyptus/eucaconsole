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


class SeleniumApi():
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

        wait.until(self.driver.find_element(By.ID, element_id), message = "Found element")

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