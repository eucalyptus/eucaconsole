from basepage import BasePage
from string import split

class Regions(BasePage):

    _region_selector_id = "selected-region"
    _region_dropdown_id = "region-dropdown"

    def __init__(self, tester):
        """
        :type tester: GuiTester
        :param tester:
        """
        self.tester = tester

    def select_region(self, region):
        self.tester.click_element_by_id(region)

    def get_region_list(self):
        """
        Gets availability zone list.
        """
        self.tester.click_element_by_id(self._region_selector_id)
        list = self.tester.store_text_by_id(self._region_dropdown_id)
        list = str(list)
        az_list = list.split()
        return az_list
