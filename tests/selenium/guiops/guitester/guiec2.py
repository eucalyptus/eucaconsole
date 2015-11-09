from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.loginpage import LoginPage
from pages.keypair.keypairdetail import KeypairDetailPage
from pages.keypair.keypair_lp import KeypairLanding
from pages.instance.instance_lp import InstanceLanding
from pages.volume.volume_view import VolumeLanding
from pages.volume.volume_detail import VolumeDetailPage
from pages.snapshot.snapshot_detail import SnapshotDetailPage
from pages.snapshot.snapshot_lp import SnapshotLanding
from pages.snapshot.create_snapshot import CreateSnapshotPage
from pages.instance.instancedetail import InstanceDetailPage
from pages.image.image_lp import ImageLanding
from pages.image.image_detail import ImageDetailPage
from pages.security_group.security_group_lp import SecurityGroupLanding
from pages.security_group.security_group_detail import SecurityGroupDetailPage
from dialogs.security_group_dialogs import CreateScurityGroupDialog, DeleteScurityGroupDialog
from dialogs.keypair_dialogs import CreateKeypairDialog, DeleteKeypairModal, ImportKeypairDialog
from dialogs.instance_dialogs import LaunchInstanceWizard, LaunchMoreLikeThisDialog, TerminateInstanceModal, TerminateAllInstancesModal
from dialogs.volume_dialogs import CreateVolumeDialog, DeleteVolumeModal, AttachVolumeModalSelectInstance, AttachVolumeModalSelectVolume, DetachVolumeModal
from dialogs.snapshot_dialogs import CreateSnapshotModal, DeleteSnapshotModal, RegisterSnapshotAsImageModal
from dialogs.image_dialogs import RemoveImageFromCloudDialog
import logging

logger = logging.getLogger('testlogger')
hdlr = logging.FileHandler('/tmp/testlog.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.setLevel(logging.WARNING)

class GuiEC2(GuiTester):

    def __init__(self, console_url, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        super(GuiEC2, self).__init__(console_url, webdriver_url=webdriver_url, sauce=sauce, browser=browser, version=version, platform=platform)

    def set_implicit_wait(self, time_to_wait):
        """
        Sets implicit wait to time_to_wait
        :param time_to_wait:
        """
        self.driver.implicitly_wait(time_to_wait)

    def set_all_pages_to_list_view(self):
        pass

    def set_all_pages_to_tile_view(self):
        pass

    def goto_images_page_via_nav(self):
        BasePage(self).goto_images_view_via_menu()
        ImageLanding(self)

    def create_keypair_from_dashboard(self, keypair_name):
        """
        Navigates to Dashboard via menu, creates keypair. Verifies keypair visible on Keypair View page.
        :param keypair_name:
        """
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_keypair_link_from_dashboard()
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self, keypair_name)

    def create_keypair_from_keypair_view_page(self, keypair_name):
        """
        Navigates from Dashboard to keypair landing page via menu. Creates keypair, verifies keypair detail page is loaded after keypair creation.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairLanding(self).click_create_keypair_button_on_view_page()
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self, keypair_name)

    def import_keypair(self, keypair, keypair_name):
        """
        Navigates to Keypair View via menu. Imports keypair. Verifies keypair visible on Keypair View page.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairLanding(self).click_import_keypair_button()
        ImportKeypairDialog(self).import_keypair(keypair, keypair_name)
        KeypairDetailPage(self, keypair_name)

    def delete_keypair_from_detail_page(self, keypair_name):
        """
        Navigates to Keypair View via menu, finds keypair, goes to keypair detail page via keypair name link. Deletes keypair.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairLanding(self).click_keypair_link_on_view_page(keypair_name)
        KeypairDetailPage(self, keypair_name).click_action_delete_keypair_on_detail_page()
        DeleteKeypairModal(self).click_delete_keypair_submit_button()
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairLanding(self).verify_keypair_not_present_on_view_page(keypair_name)

    def delete_keypair_from_view_page(self, keypair_name):
        """
        Navigates to Keypair View via menu. Deletes keypair from view page. Verifies keypair was removed from view page.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairLanding(self).click_action_delete_keypair_on_view_page(keypair_name)
        DeleteKeypairModal(self).click_delete_keypair_submit_button()
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairLanding(self).verify_keypair_not_present_on_view_page(keypair_name)

    def create_security_group_from_dashboard(self, s_group_name, s_group_description):
        """
        Creates security group from dashboard without adding rules or tags.
        :param s_group_name:
        :param s_group_description:
        """
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_s_group_link_from_dashboard()
        CreateScurityGroupDialog(self).create_s_group(s_group_name, s_group_description)
        s_group_id = SecurityGroupDetailPage(self, s_group_name).get_s_group_id()
        return {'s_group_name': s_group_name, 's_group_id':s_group_id}

    def add_tcp_22_rule_to_s_group(self, s_group_name, s_group_id):
        """
        Navigates to security group detail page. Opens TCP 22 port to user's IP.
        :param s_group_name:
        :param s_group_id:
        """
        BasePage(self).goto_security_groups_view_via_menu()
        SecurityGroupLanding(self).click_action_view_s_group_details_on_view_page(s_group_id)
        SecurityGroupDetailPage(self, s_group_name).add_rule_to_s_group_open_to_my_ip("TCP port 22")

    def add_ldap_rule_to_s_group(self, s_group_name, s_group_id):
        """
        Navigates to security group detail page. Opens TCP 389 port to all addresses.
        :param s_group_name:
        :param s_group_id:
        """
        BasePage(self).goto_security_groups_view_via_menu()
        SecurityGroupLanding(self).click_action_view_s_group_details_on_view_page(s_group_id)
        SecurityGroupDetailPage(self, s_group_name).add_rule_to_s_group_open_to_all_addresses("TCP port 389")

    def add_custom_tcp_rule_to_s_group(self, s_group_name, s_group_id):
        """
        Navigates to security group detail page. Opens TCP port 22-3389 to default group.
        :param s_group_name:
        :param s_group_id:
        """
        BasePage(self).goto_security_groups_view_via_menu()
        SecurityGroupLanding(self).click_action_view_s_group_details_on_view_page(s_group_id)
        SecurityGroupDetailPage(self, s_group_name).add_custom_tcp_rule_open_to_default_group("22","3389")

    def create_security_group_from_view_page(self, s_group_name, s_group_description):
        """
        Creates security group from S. groups view page without adding rules or tags.
        :param s_group_name:
        :param s_group_description:
        """
        BasePage(self).goto_security_groups_view_via_menu()
        SecurityGroupLanding(self).click_create_new_s_group_button()
        CreateScurityGroupDialog(self).create_s_group(s_group_name, s_group_description)
        s_group_id = SecurityGroupDetailPage(self, s_group_name).get_s_group_id()
        return {'s_group_name': s_group_name, 's_group_id':s_group_id}

    def create_sesecurity_group_with_rules(self, s_group_name, s_group_description, rule_open_to_all, rule_open_to_default_group, rule_open_to_default_group_port_begin, rule_open_to_default_group_port_end):
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_s_group_link_from_dashboard()
        CreateScurityGroupDialog(self).create_s_group_with_rules(s_group_name, s_group_description, rule_open_to_all, rule_open_to_default_group, rule_open_to_default_group_port_begin, rule_open_to_default_group_port_end)
        s_group_id = SecurityGroupDetailPage(self, s_group_name).get_s_group_id()
        return {'s_group_name': s_group_name, 's_group_id':s_group_id}

    def delete_security_group_from_view_page(self, sgroup_name, s_group_id):
        """
        Navigates to security group view page. Deletes security group from view page.
        :param sgroup_name:
        :param s_group_id:
        """
        BasePage(self).goto_security_groups_view_via_menu()
        SecurityGroupLanding(self).click_action_delete_s_group_on_view_page(s_group_id)
        DeleteScurityGroupDialog(self).delete_s_group()
        SecurityGroupLanding(self).verify_s_group_not_present(sgroup_name)

    def delete_security_group_from_detail_page(self, sgroup_name, s_group_id):
        """
        Navigates to security group detail page. Deletes security group.
        :param sgroup_name:
        :param s_group_id:
        """
        BasePage(self).goto_security_groups_view_via_menu()
        SecurityGroupLanding(self).click_action_view_s_group_details_on_view_page(s_group_id)
        SecurityGroupDetailPage(self, sgroup_name).click_action_delete_s_group_on_detail_page()
        DeleteScurityGroupDialog(self).delete_s_group()
        SecurityGroupLanding(self).verify_s_group_not_present(sgroup_name)

    def launch_instance_from_dashboard(self, image="centos", availability_zone=None, instance_type="t1.micro",
                                       number_of_of_instances=None, instance_name=None, key_name="None (advanced option)",
                                       security_group="default", user_data=None, monitoring=False, private_addressing=False, timeout_in_seconds=240):
        """
        Navigates to dashboard via menu. Launches instance.
        :param image:
        :param availability_zone:
        :param instance_type:
        :param number_of_of_instances:
        :param instance_name:
        :param key_name:
        :param security_group:
        :param user_data:
        :param monitoring:
        :param private_addressing:
        """
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_launch_instance_button_from_dashboard()
        LaunchInstanceWizard(self).launch_instance(image=image, availability_zone=availability_zone, instance_type=instance_type,
                                                          number_of_of_instances=number_of_of_instances, instance_name=instance_name, key_name=key_name,
                                                          security_group=security_group, user_data=user_data, monitoring=monitoring, private_addressing=private_addressing)
        instance_id = InstanceLanding(self).get_id_of_newly_launched_instance()
        InstanceLanding(self).goto_instance_detail_page_via_link(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).verify_instance_is_in_running_state(timeout_in_seconds=timeout_in_seconds)
        return {'instance_name': instance_name, 'instance_id':instance_id}

    def launch_instance_from_instance_view_page(self, image = "centos",availability_zone = None,
                                               instance_type = "t1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)",
                                               number_of_of_instances = None, instance_name = None, key_name = "None (advanced option)",
                                               security_group = "default", user_data=None, monitoring=False, private_addressing=False, timeout_in_seconds=240):
        """
        Navigates to instance view page via menu. Launches instance.
        :param image:
        :param availability_zone:
        :param instance_type:
        :param number_of_of_instances:
        :param instance_name:
        :param key_name:
        :param security_group:
        :param user_data:
        :param monitoring:
        :param private_addressing:
        """
        BasePage(self).goto_instances_via_menu()
        InstanceLanding(self).click_action_launch_instance_on_landing_page()
        LaunchInstanceWizard(self).launch_instance(image, availability_zone, instance_type,
                                                    number_of_of_instances, instance_name, key_name,
                                                    security_group, user_data, monitoring, private_addressing)
        instance_id = InstanceLanding(self).get_id_of_newly_launched_instance()
        InstanceLanding(self).goto_instance_detail_page_via_link(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).verify_instance_is_in_running_state(timeout_in_seconds=timeout_in_seconds)
        return {'instance_name': instance_name, 'instance_id':instance_id}

    def launch_instance_from_image_view_page(self, image_id_or_type, availability_zone = None,
                                               instance_type = "t1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)",
                                               number_of_of_instances = None, instance_name = None, key_name = "None (advanced option)",
                                               security_group = "default", user_data=None, monitoring=False, private_addressing=False, timeout_in_seconds=240):
        """
        Navigates to image view page via menu. Launches instance from given image.
        :param image_id_or_type:
        :param availability_zone:
        :param instance_type:
        :param number_of_of_instances:
        :param instance_name:
        :param key_name:
        :param security_group:
        :param user_data:
        :param monitoring:
        :param private_addressing:
        """

        BasePage(self).goto_images_view_via_menu()
        ImageLanding(self).click_action_launch_instance(image_id_or_type)
        LaunchInstanceWizard(self).launch_instance_step2(availability_zone, instance_type,
                                                        number_of_of_instances, instance_name, key_name,
                                                        security_group, user_data, monitoring, private_addressing)
        instance_id = InstanceLanding(self).get_id_of_newly_launched_instance()
        InstanceLanding(self).goto_instance_detail_page_via_link(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).verify_instance_is_in_running_state(timeout_in_seconds=timeout_in_seconds)
        return {'instance_name': instance_name, 'instance_id':instance_id}

    def launch_more_like_this_from_view_page(self, inatance_id, instance_name=None, user_data=None, monitoring=False, private_addressing=False, timeout_in_seconds=240):
        """
        Navigates to instances view page. Launches an instance like given instance.
        :param inatance_id:
        :param instance_name:
        :param user_data:
        :param monitoring:
        :param private_addressing:
        """
        BasePage(self).goto_instances_via_menu()
        InstanceLanding(self).click_action_launch_more_like_this(inatance_id)
        LaunchMoreLikeThisDialog(self).launch_more_like_this(instance_name, user_data, monitoring, private_addressing)
        instance_id = InstanceLanding(self).get_id_of_newly_launched_instance()
        InstanceLanding(self).goto_instance_detail_page_via_link(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).verify_instance_is_in_running_state(timeout_in_seconds=timeout_in_seconds)
        return {'instance_name': instance_name, 'instance_id':instance_id}

    def launch_more_like_this_from_detail_page(self, base_instance_id, instance_name=None, user_data=None, monitoring=False, private_addressing=False, timeout_in_seconds=240):
        """
        Navigates to instance detail page. Launches an instance like given instance.
        :param inatance_id:
        :param instance_name:
        :param user_data:
        :param monitoring:
        :param private_addressing:
        """
        BasePage(self).goto_instances_via_menu()
        base_instance_name=InstanceLanding(self).get_instance_name(base_instance_id)
        InstanceLanding(self).goto_instance_detail_page_via_actions(base_instance_id)
        InstanceDetailPage(self, base_instance_id, base_instance_name).click_action_launch_more_like_this()
        LaunchMoreLikeThisDialog(self).launch_more_like_this(instance_name, user_data, monitoring, private_addressing)
        instance_id = InstanceLanding(self).get_id_of_newly_launched_instance()
        InstanceLanding(self).goto_instance_detail_page_via_link(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).verify_instance_is_in_running_state(timeout_in_seconds=timeout_in_seconds)
        return {'instance_name': instance_name, 'instance_id':instance_id}

    def terminate_instance_from_view_page(self, instance_id, instance_name=None):
        """
        Navigates to view page, terminates instance.
        :param instance_name:
        :param instance_id:
        """
        BasePage(self).goto_instances_via_menu()
        InstanceLanding(self).click_action_terminate_instance_on_view_page(instance_id)
        TerminateInstanceModal(self).click_terminate_instance_submit_button(instance_id)
        InstanceLanding(self).goto_instance_detail_page_via_link(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).verify_instance_is_terminated()

    def terminate_instance_from_detail_page(self, instance_id):
        """
        Navigates to detail page, terminates instance.
        :param instance_id:
        """

        BasePage(self).goto_instances_via_menu()
        instance_name=InstanceLanding(self).get_instance_name(instance_id)
        InstanceLanding(self).goto_instance_detail_page_via_actions(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).click_terminate_instance_action_item_from_detail_page()
        TerminateInstanceModal(self).click_terminate_instance_submit_button(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).verify_instance_is_terminated()

    def batch_terminate_all_instances(self):
        """
        Navigates to instances view page and terminates all instances
        """

        BasePage(self).goto_instances_via_menu()
        InstanceLanding(self).click_terminate_all_instances_button()
        TerminateAllInstancesModal(self).click_terminate_all_instances_submit_button()
        InstanceLanding(self).verify_there_are_no_running_instances()

    def create_volume_from_view_page(self, volume_name=None, create_from_snapshot=False, snapshot_id = None, volume_size=None, availability_zone=None, timeout_in_seconds=240):
        """
        Navigates to volumes view page and creates volume.
        :param volume_name:
        :param create_from_snapshot:
        :param snapshot_id:
        :param volume_size:
        :param availability_zone:
        """
        BasePage(self).goto_volumes_view_via_menu()
        VolumeLanding(self).click_create_volume_btn_on_landing_page()
        CreateVolumeDialog(self).create_volume(volume_name, create_from_snapshot, snapshot_id, volume_size, availability_zone)
        VolumeDetailPage(self).verify_volume_status_is_available(timeout_in_seconds=timeout_in_seconds)
        volume = VolumeDetailPage(self).get_volume_name_and_id()
        print volume
        return volume

    def create_volume_from_dashboard(self, volume_name=None, create_from_snapshot=False,snapshot_id=None, volume_size=None, availability_zone=None, timeout_in_seconds=240 ):
        """
        Navigates to dashboard and creates volume.
        :param volume_name:
        :param create_from_snapshot:
        :param snapshot_id:
        :param volume_size:
        :param availability_zone:
        :param timeout_in_seconds:
        """
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_volume_link()
        CreateVolumeDialog(self).create_volume(volume_name=volume_name, create_from_snapshot=create_from_snapshot, snapshot_id=snapshot_id, volume_size=volume_size, availability_zone=None)
        VolumeDetailPage(self).verify_volume_status_is_available(timeout_in_seconds=timeout_in_seconds)
        volume = VolumeDetailPage(self).get_volume_name_and_id()
        print volume
        return volume

    def delete_volume_from_view_page(self, volume_id, timeout_in_seconds=240):
        """
        Navigates to volumes view page and deletes volume.
        :param timeout_in_seconds:
        :param volume_id:
        """
        BasePage(self).goto_volumes_view_via_menu()
        VolumeLanding(self).click_action_delete_volume_on_view_page(volume_id)
        DeleteVolumeModal(self).delete_volume()
        VolumeLanding(self).verify_volume_status_is_deleted(volume_id, timeout_in_seconds)

    def delete_volume_from_detail_page(self, volume_id, volume_name=None, timeout_in_seconds=240):
        """
        Navigates to volume detail page and deletes volume. Waits for volume state to become 'deleted' on landing page.
        :param timeout_in_seconds:
        :param volume_id:
        :param volume_name:
        """
        BasePage(self).goto_volumes_view_via_menu()
        VolumeLanding(self).goto_volume_detail_page_via_actions(volume_id)
        VolumeDetailPage(self).verify_volume_detail_page_loaded(volume_id, volume_name)
        VolumeDetailPage(self).click_action_delete_volume_on_detail_page()
        DeleteVolumeModal(self).delete_volume()
        VolumeLanding(self).verify_volume_status_is_deleted(volume_id, timeout_in_seconds)

    def attach_volume_from_volume_lp(self, instance_id, volume_id, device=None, timeout_in_seconds=240):
        """
        Navigates to volumes landing page, attaches a given volume to a given instance.
        :param device:
        :param timeout_in_seconds:
        :param instance_id:
        :param volume_id:
        """
        BasePage(self).goto_volumes_view_via_menu()
        VolumeLanding(self).click_action_attach_to_instance(volume_id)
        AttachVolumeModalSelectInstance(self).attach_volume(instance_id, device)
        VolumeLanding(self).verify_volume_status_is_attached(volume_id, timeout_in_seconds)

    def attach_volume_from_volume_detail_page(self, instance_id, volume_id, device=None, timeout_in_seconds=240):
        """
        Navigates to volume detail page, attaches volume to instance.
        :param instance_id:
        :param volume_id:
        :param device:
        :param timeout_in_seconds:
        """
        BasePage(self).goto_volumes_view_via_menu()
        VolumeLanding(self).goto_volume_detail_page_via_link(volume_id)
        VolumeDetailPage(self).click_action_attach_volume_on_detail_page()
        AttachVolumeModalSelectInstance(self).attach_volume(instance_id, device=device)
        VolumeDetailPage(self).verify_volume_status_is_attached(timeout_in_seconds)

    def attach_volume_from_instance_detail_page(self, volume_id, instance_id, instance_name=None, device=None, timeout_in_seconds=240):
        """
        Navigates to instance detail page and attaches volume.
        :param instance_id:
        :param volume_id:
        :param device:
        :param timeout_in_seconds:
        """
        BasePage(self).goto_instances_via_menu()
        InstanceLanding(self).goto_instance_detail_page_via_link(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).click_action_attach_volume()
        AttachVolumeModalSelectVolume(self).attach_volume(volume_id, device)
        InstanceDetailPage(self, instance_id).verify_volume_is_attached(volume_id, timeout_in_seconds)

    def attach_volume_from_instance_lp(self, volume_id, instance_id, instance_name=None, device=None, timeout_in_seconds=240):
        """
        Navigates to instance landing page. Attaches volume.
        :param volume_id:
        :param instance_id:
        :param instance_name:
        :param device:
        :param timeout_in_seconds:
        """
        BasePage(self).goto_instances_via_menu()
        InstanceLanding(self).click_action_manage_volumes_on_view_page(instance_id)
        InstanceDetailPage(self, instance_id, instance_name).click_action_attach_volume()
        AttachVolumeModalSelectVolume(self).attach_volume(volume_id, device)
        InstanceDetailPage(self, instance_id).verify_volume_is_attached(volume_id, timeout_in_seconds)

    def detach_volume_from_volumes_lp(self, volume_id, timeout_in_seconds=240):
        """
        Navigate to volumes landing page. Detach volume.
        :param instance_id:
        :param volume_id:
        """
        BasePage(self).goto_volumes_view_via_menu()
        VolumeLanding(self).click_action_detach_volume_on_view_page(volume_id)
        DetachVolumeModal(self).detach_volume(volume_id)
        VolumeLanding(self).verify_volume_status_is_available(volume_id, timeout_in_seconds)

    def detach_volume_from_volume_detail_page(self, volume_id, timeout_in_seconds):
        """
        Navigates to volume detail page. Detaches volume from instance. Verifies volume is in available state.
        :param volume_id:
        :param timeout_in_seconds:
        """
        NotImplementedError

    def detach_volume_from_instance_detail_page(self, volume_id, instance_id,  timeout_in_seconds):
        """
        Navigates to instance detail page. Detaches a given volume. Verifies volume is in available state.
        :param volume_id:
        :param instance_id:
        :param timeout_in_seconds:
        """
        NotImplementedError

    def detach_volume_from_instance_lp(self, volume_id, instance_id,  timeout_in_seconds):
        """
        Navigates to instance landing page. Goes to volumes tab by "Manage Volumes" action. Detaches given volume. Verifies volume is in available state.
        :param volume_id:
        :param instance_id:
        :param timeout_in_seconds:
        """
        NotImplementedError

    def create_snapshot_on_volumes_view_page(self, volume_id, snapshot_name=None, snapshot_description=None, timeout_in_seconds=240):
        """
        Navigates to volumes view page and creates a snapshot of a volume.
        :param snapshot_name:
        :param snapshot_description:
        :param timeout_in_seconds:
        :param volume_id:
        """
        BasePage(self).goto_volumes_view_via_menu()
        VolumeLanding(self).click_action_manage_snaspshots(volume_id)
        VolumeDetailPage(self).click_create_snapshot_from_volume_tile(volume_id)
        CreateSnapshotModal(self).create_snapshot(snapshot_name, snapshot_description)
        VolumeDetailPage(self).goto_detail_page_of_newly_created_snapshot(volume_id)
        snapshot=SnapshotDetailPage(self).get_snapshot_name_and_id(snapshot_name)
        SnapshotDetailPage(self).verify_snapshot_status_is_completed(timeout_in_seconds)
        print snapshot
        return snapshot

    def create_snapshot_on_volume_detail_page(self, volume_id, snapshot_name=None, snapshot_description=None, timeout_in_seconds=240):
        """
        Navigates to volume detail page and creates a snapshot.
        :param timeout_in_seconds:
        :param volume_id:
        :param snapshot_name:
        :param snapshot_description:
        """
        BasePage(self).goto_volumes_view_via_menu()
        VolumeLanding(self).goto_volume_detail_page_via_actions(volume_id)
        VolumeDetailPage(self).click_create_snapshot_from_volume_tile(volume_id)
        CreateSnapshotModal(self).create_snapshot(snapshot_name, snapshot_description)
        VolumeDetailPage(self).goto_detail_page_of_newly_created_snapshot(volume_id)
        snapshot=SnapshotDetailPage(self).get_snapshot_name_and_id(snapshot_name)
        SnapshotDetailPage(self).verify_snapshot_status_is_completed(timeout_in_seconds)
        print snapshot
        return snapshot

    def create_snapshot_on_snapshot_view_page(self, volume_id, snapshot_name=None, snapshot_description=None, timeout_in_seconds=240):
        """
        Navigates to snapshot landing page, creates snapshot.
        :param volume_id:
        :param snapshot_name:
        :param snapshot_description:
        :param timeout_in_seconds:
        """
        BasePage(self).goto_snapshots_view_via_menu()
        SnapshotLanding(self).click_create_snapshot_btn_on_view_page()
        CreateSnapshotPage(self).create_snapshot(volume_id=volume_id, snapshot_name=snapshot_name, snapshot_description=snapshot_description)
        snapshot = SnapshotDetailPage(self).get_snapshot_name_and_id(snapshot_name)
        SnapshotDetailPage(self).verify_snapshot_status_is_completed(timeout_in_seconds)
        print snapshot
        return snapshot

    def create_snapshot_from_dashboard(self, volume_id, snapshot_name=None, snapshot_description=None, timeout_in_seconds=240):
        """
        Navigates to snapshot landing page, creates snapshot.
        :param volume_id:
        :param snapshot_name:
        :param snapshot_description:
        :param timeout_in_seconds:
        """
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_snapshot_link()
        CreateSnapshotPage(self).create_snapshot(volume_id=volume_id, snapshot_name=snapshot_name, snapshot_description=snapshot_description)
        snapshot = SnapshotDetailPage(self).get_snapshot_name_and_id(snapshot_name)
        SnapshotDetailPage(self).verify_snapshot_status_is_completed(timeout_in_seconds)
        print snapshot
        return snapshot

    def delete_snapshot_from_landing_page(self, snapshot_id):
        """
        Navigates to landing page, deletes snapshot, verifies snapshot is gone from landing page.
        :param snapshot_id:
        """
        BasePage(self).goto_snapshots_view_via_menu()
        SnapshotLanding(self).click_action_delete_snapshot_on_view_page(snapshot_id)
        DeleteSnapshotModal(self).delete_snapshot()
        SnapshotLanding(self).verify_snapshot_not_present(snapshot_id)

    def delete_snapshot_from_detail_page(self, snapshot_id):
        """
        Navigates to detail page, deletes snapshot, verifies snapshot is gone from landing page.
        :param snapshot_id:
        """
        BasePage(self).goto_snapshots_view_via_menu()
        SnapshotLanding(self).goto_snapshot_detail_page_via_link(snapshot_id)
        SnapshotDetailPage(self).click_action_delete_snapshot_on_detail_page()
        DeleteSnapshotModal(self).delete_snapshot()
        SnapshotLanding(self).verify_snapshot_not_present(snapshot_id)

    def create_volume_from_snapshot_on_snapshot_lp(self, snapshot_id, volume_name=None, availability_zone=None, volume_size=None, timeout_in_seconds=240):
        """
        Navigates to snapshot landing page. Goes to "create volume from snapshot" in the actions menu. Creates volume from snapshot.
        :param snapshot_id:
        :param volume_name:
        :param availability_zone:
        :param volume_size:
        :param timeout_in_seconds:
        """
        BasePage(self).goto_snapshots_view_via_menu()
        SnapshotLanding(self).click_action_create_volume_from_snapshot(snapshot_id)
        CreateVolumeDialog(self).create_volume(volume_name, volume_size=volume_size, availability_zone=availability_zone, timeout_in_seconds=timeout_in_seconds)
        VolumeDetailPage(self).verify_volume_status_is_available(timeout_in_seconds=timeout_in_seconds)
        volume = VolumeDetailPage(self).get_volume_name_and_id()
        print volume
        return volume

    def create_volume_from_snapshot_on_snapshot_detail_page(self, snapshot_id, volume_name=None, availability_zone=None, volume_size=None, timeout_in_seconds=240):
        """
        Navigates to snapshot detail page. Goes to "create volume from snapshot" in the actions menu. Creates volume from snapshot.
        :param snapshot_id:
        :param volume_name:
        :param availability_zone:
        :param volume_size:
        :param timeout_in_seconds:
        """
        BasePage(self).goto_snapshots_view_via_menu()
        SnapshotLanding(self).goto_snapshot_detail_page_via_link(snapshot_id)
        SnapshotDetailPage(self).click_action_create_volume_from_snapshot_on_detail_page()
        CreateVolumeDialog(self).create_volume(volume_name, volume_size=volume_size, availability_zone=availability_zone, timeout_in_seconds=timeout_in_seconds)
        VolumeDetailPage(self).verify_volume_status_is_available(timeout_in_seconds=timeout_in_seconds)
        volume = VolumeDetailPage(self).get_volume_name_and_id()
        print volume
        return volume

    def delete_snapshot_from_tab_on_volume_detail_page(self):
        NotImplementedError

    def delete_snapshot_from_lp(self):
        NotImplementedError

    def register_snapshot_as_an_image_from_snapshot_landing_page(self, snapshot_id, image_name, description=None, delete_on_terminate=True, register_as_windows_image=False):
        BasePage(self).goto_snapshots_view_via_menu()
        SnapshotLanding(self).click_action_register_as_image(snapshot_id)
        RegisterSnapshotAsImageModal(self).register_as_image(name=image_name, description=description, delete_on_terminate=delete_on_terminate, register_as_windows_image=register_as_windows_image)
        image_id = ImageDetailPage(self).get_image_id()
        image = {'image_name': image_name, 'image_id': image_id}
        print image
        return image

    def remove_image_from_cloud_on_images_lp(self, image_id, delete_associated_snapshot=False):
        BasePage(self).goto_images_view_via_menu()
        ImageLanding(self).click_action_remove_image_from_cloud(image_id)
        RemoveImageFromCloudDialog(self).remove_image(delete_associated_snapshot)

    def register_snapshot_as_an_image_from_snapshot_detail_page(self):
        NotImplementedError()

    def allocate_ip_from_eip_lp(self):
        NotImplementedError

    def allocate_eip_from_dashboard(self):
        NotImplementedError

    def release_eip_from_eip_lp(self):
        NotImplementedError

    def release_eip_from_eip_detail_page(self):
        NotImplementedError

    def associate_eip_from_eip_lp(self):
        NotImplementedError

    def associate_eip_from_instances_lp(self):
        NotImplementedError

    def associate_eip_from_instance_detail_page(self):
        NotImplementedError

    def associate_eip_from_eip_detail_page(self):
        NotImplementedError

    def disassociate_eip_from_eip_lp(self):
        NotImplementedError

    def disassociate_eip_from_eip_detail_page(self):
        NotImplementedError

    def disassociate_ip_from_instance_detail_page(self):
        NotImplementedError

    def disassociate_eip_from_instances_lp(self):
        NotImplementedError












