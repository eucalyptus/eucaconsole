from basepage import BasePage
from guitester.guitester import GuiTester


class LandingPage(BasePage):

    _refresh_button_id = "refresh-btn"
    _item_count_css = "strong.ng-binding"
    _page_title_id = "pagetitle"
    _dashboard_icon_css = "i.fi-home"
    _list_view_icon = "a#tableview-button"
    _grid_view = "a#gridview-button"

    def __init__(self, tester):
        assert isinstance(tester, GuiTester)
        self.tester = tester


    def goto_dashboard_via_icon(self):
        self.tester.click_on_visible_by_css_selector(self._dashboard_icon_css)




