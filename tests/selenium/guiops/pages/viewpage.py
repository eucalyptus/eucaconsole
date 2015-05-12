from basepage import BasePage

class ViewPage(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _refresh_button_id = "refresh-btn"
    _item_count_css = "strong.ng-binding"
    _page_title_id = "pagetitle"
    _dashboard_icon_css = "i.fi-home"
    _list_view_icon = "a#tableview-button"
    _grid_view = "a#gridview-button"
    _landing_page_title_id = "pagetitle"

    def goto_dashboard_via_icon(self):
        self.tester.click_element_by_css(self._dashboard_icon_css)




