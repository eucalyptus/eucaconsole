from pages.detailpage import DetailPage


class VolumeDetailPage(DetailPage):
    VOLUME_MONITORING_CHARTS_LIST = [
        {'metric': 'VolumeReadBytes', 'statistic': 'Sum'},
        {'metric': 'VolumeWriteBytes', 'statistic': 'Sum'},
        {'metric': 'VolumeReadOps', 'statistic': 'Sum'},
        {'metric': 'VolumeWriteOps', 'statistic': 'Sum'},
        {'metric': 'VolumeQueueLength', 'statistic': 'Average'},
        {'metric': 'VolumeIdleTime', 'statistic': 'Sum'},
        {'metric': 'VolumeReadBytes', 'statistic': 'Average'},
        {'metric': 'VolumeWriteBytes', 'statistic': 'Average'},
        {'metric': 'VolumeTotalReadTime', 'statistic': 'Average'},
        {'metric': 'VolumeTotalWriteTime', 'statistic': 'Average'},
    ]

    def __init__(self, tester):
        self.tester = tester
        self.print_test_context()

    _volume_detail_page_title = "Details for volume: {0}"
    _delete_volume_action_menuitem_id = "delete-volume-action"
    _attach_volume_action_menuitem_id = "attach-volume-action"
    _unattached_notice_id = 'volume-unattached-notice'
    _charts_container_id = 'charts-container'
    _volume_status_css = "[class='label radius status {0}']"  # volume status is required
    _create_snapshot_tile_css = "#create-snapshot>a"
    _general_tab_css = '[href="/volumes/{0}"]'  # volume_id is required
    _snapshots_tab_css = "[href='/volumes/{0}/snapshots']"  # volume_id is required
    _monitoring_tab_css = "[href='/volumes/{0}/monitoring']"  # volume_id is required
    _active_tab_css = "dd.active"
    _id_link_in_tile_of_newly_created_snapshot_css = '[class="ng-binding"]'

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
        self.tester.verify_visible_by_css(self._volume_status_css.format("available"), timeout_in_seconds)

    def verify_volume_status_is_attached(self, timeout_in_seconds):
        self.tester.verify_visible_by_css(self._volume_status_css.format("attached"), timeout_in_seconds)

    def get_volume_name_and_id(self):
        name_and_id = str(self.tester.store_text_by_css(DetailPage(self)._resource_name_and_id_css))
        if len(name_and_id) > 12:
            volume_id = name_and_id[-13:-1]
            volume_name = name_and_id[1:-15]
        else:
            volume_name = None
            volume_id = name_and_id
        return {'volume_name': volume_name, 'volume_id': volume_id}

    def goto_snapshots_tab(self, volume_id):
        """
        Checks if Snapshot tab is already open. Opens snapshot tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab != "Snapshots":
            self.tester.click_element_by_css(self._snapshots_tab_css.format(volume_id))

    def goto_monitoring_tab(self, volume_id):
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab != "Monitoring":
            self.tester.click_element_by_css(self._monitoring_tab_css.format(volume_id))

    def verify_attach_notice_on_volume_monitoring_page(self, volume_id):
        self.tester.wait_for_element_present_by_id(self._unattached_notice_id)

    def verify_charts_on_volume_monitoring_page(self, volume_id):
        self.tester.wait_for_element_present_by_id(self._charts_container_id)
        for chart in self.VOLUME_MONITORING_CHARTS_LIST:
            chart_id = 'cwchart-{0}-{1}'.format(chart.get('metric'), chart.get('statistic'))
            self.tester.wait_for_element_present_by_id(chart_id)

    def click_create_snapshot_from_volume_tile(self, volume_id):
        self.goto_snapshots_tab(volume_id)
        self.tester.click_element_by_css(self._create_snapshot_tile_css)

    def goto_detail_page_of_newly_created_snapshot(self, volume_id):
        self.goto_snapshots_tab(volume_id)
        self.tester.click_element_by_css(self._id_link_in_tile_of_newly_created_snapshot_css)

    def verify_snapshot_tile_not_present(self):
        raise NotImplementedError
