/**
 * @fileOverview Common JS for Eucalyptus Management Console
 * @requires AngularJS
 *
 */

angular.module('EucaConsoleUtils', [])
.service('eucaUnescapeJson', function() {
    /**
     * Unescape JSON escaped server-side via BaseView.escape_json() custom method
     * @param {string} jsonString - JSON string, with single/double quotes and backslashes escaped.
     * @return {string} unescaped JSON string
     */
    return function(jsonString) {
        return jsonString.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
    };
})
.service('handleError', function() {
    /**
     * Provide generic error handling in the browser for XHR calls. 
     */
    return function(data, status) {
        var errorMsg = data['message'] || '';
        if (status === 403) {
            if (errorMsg.indexOf('Not authorized') == -1) {
                $('#timed-out-modal').foundation('reveal', 'open');
            }
            // else, fallthrough and display message
        }
        Notify.failure(errorMsg);
    };
})
.service('handleErrorS3', function() {
    /**
     * Provide generic error handling in the browser for XHR calls to Object Storage. 
     */
    return function(data, status) {
        var errorMsg = data['message'] || '';
        if (status === 403 || status === 400) {
            if (errorMsg.indexOf('Not authorized') == -1) {
                $('#timed-out-modal').foundation('reveal', 'open');
            }
            // else, fallthrough and display message
        }
        Notify.failure(errorMsg);
    };
});
