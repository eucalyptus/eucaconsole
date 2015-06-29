from basepage import BasePage

class ViewPage(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _refresh_button_id = "refresh-btn"
    _item_count_css = ".items-found>.ng-binding"
    _page_title_id = "pagetitle"
    _dashboard_icon_css = "i.fi-home"
    _list_view_icon = "a#tableview-button"
    _grid_view = "a#gridview-button"
    _view_page_title_id = "pagetitle"
    _search_input_field_css = ".search-input"
    _resource_action_menu_id = "table-item-dropdown_{0}"  # resource id or name if no id required

    def goto_dashboard_via_icon(self):
        self.tester.click_element_by_css(self._dashboard_icon_css)




