/**
 * @fileOverview Common JS for Eucalyptus Management Console
 * @requires AngularJS
 *
 */

angular.module('EucaConsoleUtils', ['CustomFilters', 'ngSanitize'])
.service('eucaUnescapeJson', function() {
    /**
     * Unescape JSON escaped server-side via BaseView.escape_json() custom method
     * @param {string} jsonString - JSON string, with single/double quotes, backslashes, and curly braces escaped.
     * @return {string} unescaped JSON string
     */
    return function(jsonString) {
        return jsonString.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
    };
})
.service('eucaOptionsArray', function () {
    /**
     * Return an array of objects with value/label keys for select drop-downs based on ng-options
     * @param {array} optionsList - Array of value, label arrays (e.g. [['value1', 'label1'], ['value2', 'label2']]
     * @return {array} Array of objects with value/label keys (e.g. [{'value': 'value1', 'label': 'label1'}, ...]
     */
    return function(optionsList) {
        var optionsArray = [];
        angular.forEach(optionsList, function(item) {
            optionsArray.push({value: item[0], label: item[1]});
        });
        return optionsArray;
    };
})
.service('eucaHandleError', function() {
    /**
     * Provide generic error handling in the browser for XHR calls. 
     */
    return function(data, status) {
        var errorMsg = data.message || '';
        if (status === 403) {
            if (errorMsg.indexOf('Not authorized') == -1) {
                $('#timed-out-modal').foundation('reveal', 'open');
            }
            // else, fallthrough and display message
        }
        Notify.failure(errorMsg);
    };
})
.service('eucaHandleErrorNoNotify', function() {
    /**
     * Provide generic error handling in the browser for XHR calls. 
     */
    return function(data, status) {
        var errorMsg = data.message || '';
        if (status === 403) {
            if (errorMsg.indexOf('Not authorized') == -1) {
                $('#timed-out-modal').foundation('reveal', 'open');
            }
        }
    };
})
.service('eucaHandleErrorS3', function() {
    /**
     * Provide generic error handling in the browser for XHR calls to Object Storage. 
     */
    return function(data, status) {
        var errorMsg = data.message || '';
        if (status === 403 || status === 400) {
            if (errorMsg.indexOf('Not authorized') == -1) {
                $('#timed-out-modal').foundation('reveal', 'open');
            }
            // else, fallthrough and display message
        }
        Notify.failure(errorMsg);
    };
});

angular.module('EucaConsoleUtils');
