/**
 * @fileOverview JS for Eucalyptus Management Console
 * @requires jQuery
**/


(function($) {
    // Initialize all Zurb Foundation components
    $(document).foundation({
        offcanvas : {
            open_method: 'overlap_single', 
        }
    });

    $(document).ready(function () {

        // Notifications display
        var notification = $('#notifications');
        if (notification.find('.alert').length === 0) {
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

        // hide nav on login screen
        if ($('#login-wrapper').length > 0) {
            $('.left-nav').remove();
            $('.inner-wrap').css('padding-left', '0');
        }
        else {
            // set active selection in nav
            var path = window.location.pathname;
            var screen = '';
            var i;
            if (path === '/') {
                screen = 'dashboard';
            }
            else {
                screen = path.substring(1);
                if (screen.indexOf("/") > -1) {
                    screen = screen.substring(0, screen.indexOf("/"));
                }
            }

            var selected = $('ul.resources-nav').find("."+screen);
            $(selected).addClass('active');

            // handlers for nav expand/collapse w/ mouse
            $('.left-nav').mouseenter(expand).mouseleave(collapse);

        }
        function collapse() {
          $('.left-nav').addClass('nav-collapsed');
        }
      
        function expand() {
          $('.left-nav').removeClass('nav-collapsed');
        }
    });
})(jQuery);
