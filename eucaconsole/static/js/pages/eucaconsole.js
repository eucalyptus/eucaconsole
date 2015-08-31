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
            var recentKey = $('.username-label').text() + "recent-nav-items";
            var recentNav = [];
            if (Modernizr.localstorage) {
                var tmp = localStorage.getItem(recentKey);
                if (tmp !== null) {
                    recentNav = JSON.parse(tmp);
                }
            }
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
                else {
                    // landing page, so save to most recent
                    if (Modernizr.localstorage && ['dashboard', 'managecredentials'].indexOf(screen) === -1) {
                        for (i=0; i<recentNav.length; i++) {
                            if (recentNav[i] === screen) {
                                recentNav.splice(i, 1);
                            }
                        }
                        recentNav = [screen].concat(recentNav);
                        if (recentNav.length > 3) {
                            recentNav.pop();
                        }
                        localStorage.setItem(recentKey, JSON.stringify(recentNav));
                    }
                }
            }
            // set up most recent
            for (i=0; i<3; i++) {
                var recent = recentNav[i];
                var recentLink = $('.resources-nav').find("#resource-menuitem-recent-" + (i + 1));
                if (recent !== undefined) {
                    recentLink.attr('href', $("#resource-menuitem-" + recent).attr('href'));
                    var recentIcon = recentLink.find("i");
                    recentIcon.addClass(recent);
                    var recentLabel = recentLink.find("span");
                    recentLabel.text($('#resource-menuitem-' + recent).find('span').text());
                }
                else {
                    recentLink.remove();
                }
            }
            if (recentNav.length === 0) {
                $('#recent-nav-label').remove();
                $('#recent-nav-hr').remove();
            }

            var selected = $('ul.resources-nav').find("."+screen);
            var idx = 1;
            // do this since dashboard never gets added to recent list
            if (screen == 'dashboard') idx = 0;
            $(selected[idx]).addClass('active');
            $(selected[idx]).next().addClass('active');

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
