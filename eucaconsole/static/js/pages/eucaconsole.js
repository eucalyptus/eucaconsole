/**
 * @fileOverview JS for Eucalyptus Management Console
 * @requires jQuery
**/


(function($) {
    $(document).ready(function () {

        // Initialize all Zurb Foundation components
        $(document).foundation();

        // Notifications display
        var notification = $('#notifications');
        if (notification.find('.alert').length == 0) {
            // remove success notifications after 5 seconds
            setTimeout(function(){
                Notify.clear();
            }, 5000);
        }

        // Prevent cancel link click from displaying unsaved changes warning
        $(document).on('click', '.cancel-link', function(event) {
            window.onbeforeunload = null;
        });

        // Logout form handlers
        // Username dropdown menu
        $('#user-dropdown').find('#logout').on('click', function () {
            $('#euca-logout-form').submit();
        });
        // Session timeout notification
        $('#euca-login-button').on('click', function () {
            $('#euca-logout-form').submit();
        });

    });
})(jQuery);
