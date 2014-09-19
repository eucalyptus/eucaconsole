/**
 * @fileOverview Common JS for Eucalyptus Management Console
 *
 *
 */


var EUCACONSOLE = window.EUCACONSOLE || {};


/**
 * Unescape JSON escaped server-side via BaseView.escape_json() custom method
 * @param {string} jsonString - JSON string, with single/double quotes and backslashes escaped.
 * @return {string} escaped JSON string
 */
EUCACONSOLE.unescapeJson = function (jsonString) {
    return jsonString.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
};

