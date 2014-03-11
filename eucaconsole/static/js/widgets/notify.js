/*
 Notification package for client side events
*/
var Notify = (function() {
    var notify = {
        success: function(message) {
            $("#notifications").append($("<div>").
                append($("<div>").addClass("alert-box", '').addClass('success', '').
                text(message).append($("<a>").addClass('close').attr("href", "#").text("x").
                click( function(evt) {
                    Notify.clear();
                }))));
            setTimeout(function(){ 
                Notify.clear();
            }, 5000);
        },
        failure: function(message) {
            $("#notifications").append($("<div>").
                append($("<div>").addClass("alert-box", '').addClass('alert', '').
                text(message).append($("<a>").addClass('close').attr("href", "#").text("x").
                click( function(evt) {
                    Notify.clear();
                }))));
        },
        clear: function() {
            $("#notifications").text("");
        },
    };
    return notify;
}());
