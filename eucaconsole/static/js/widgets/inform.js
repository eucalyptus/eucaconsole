/*
 Informational dialog package for cases where in-line warnings aren't enough.
*/
var Inform = (function() {
    var inform = {
        informational: function(message, title) {
            $('#inform-modal').foundation('reveal', 'close');
            $('#inform-title').text(title);
            $('#inform-message').text(message);
            $('#inform-modal').foundation('reveal', 'open');
        },
        confirmation: function(message, yes_button_text, confirm_func, title) {
            $('#confirm-modal').foundation('reveal', 'close');
            $('#confirm-message').text(message);
            $('#confirm-btn').text(yes_button_text);
            $('#confirm-btn').attr('onclick', confirm_func);
            $('#confirm-modal').foundation('reveal', 'open');
        },
        hideAll: function() {
            $('#confirm-modal').foundation('reveal', 'close');
            $('#inform-modal').foundation('reveal', 'close');
        },
    };
    return inform;
}());
