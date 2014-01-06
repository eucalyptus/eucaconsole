/**
   * @fileOverview Common JS for Custom Filters
   * @requires AngularJS, jQuery, and Purl jQuery URL parser plugin
 * TODO: Move this to a new /static/js/utils folder
**/

angular.module('CustomFilters', []).filter('escapeURL', function() {
  return function(input) {
    return encodeURIComponent(input);
  };
});


