from basepage import BasePage


class DetailPage(BasePage):

    _detail_page_title_id = "pagetitle"
    _resource_name_and_id_css = "#pagetitle>em"
    _actions_menu_css =".actions-menu>span>a"

