from pages.detailpage import DetailPage
from string import split

class VolumeDetailPage(DetailPage):

    def __init__(self, tester):
        self.tester = tester

    _volume_detail_page_title = "Details for volume: {0}"
    _delete_volume_action_menuitem_id = "delete-volume-action"
    _attach_volume_action_menuitem_id = "attach-volume-action"
    _volume_status_css = "[class='label radius status {0}']"  # volume status is required
    _create_snapshot_tile_css = "#create-snapshot>a"
    _snapshots_tab_css = "[href='/volumes/{0}/snapshots']"  # volume_id is required
    _general_tab_css = '[href="/volumes/{0}/snapshots"]'  # volume_id is required
    _active_tab_css ="dd.active"
    _id_link_in_tile_of_newly_created_snapshot_css='[class="ng-binding"]'

    def verify_volume_detail_page_loaded(self, volume_id, volume_name):
        """
        Waits for the volume detail page title to appear; waits for actions menu to become visible.
        """
        if volume_name is None:
            volume_name_full = volume_id
        else:
            volume_name_full = volume_name + " (" + volume_id + ")"
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id, volume_name_full)
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def click_action_delete_volume_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_volume_action_menuitem_id)

    def click_action_attach_volume_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._attach_volume_action_menuitem_id)

    def verify_volume_status_is_available(self, timeout_in_seconds):
        self.tester.wait_for_visible_by_css(self._volume_status_css.format("available"), timeout_in_seconds)

    def verify_volume_status_is_attached(self, timeout_in_seconds):
        self.tester.wait_for_visible_by_css(self._volume_status_css.format("attached"), timeout_in_seconds)

    def get_volume_name_and_id(self):
        name_and_id = str(self.tester.store_text_by_css(DetailPage(self)._resource_name_and_id_css))
        volume_id = name_and_id[-13:-1]
        volume_name = name_and_id[1:-15]
        return {'volume_name': volume_name, 'volume_id': volume_id}

    def goto_snapshots_tab(self, volume_id):
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab == "General":
            self.tester.click_element_by_css(self._snapshots_tab_css.format(volume_id))
        elif tab == "Snapshots":
            pass
        else:
            print "ERROR: tab {0} not among recognized tab names.".format(tab)

    def click_create_snapshot_from_volume_tile(self, volume_id):
        self.goto_snapshots_tab(volume_id)
        self.tester.click_element_by_css(self._create_snapshot_tile_css)

    def goto_detail_page_of_newly_created_snapshot(self, volume_id):
        self.goto_snapshots_tab(volume_id)
        self.tester.click_element_by_css(self._id_link_in_tile_of_newly_created_snapshot_css)





