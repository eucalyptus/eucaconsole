/**
 * @fileOverview CloudWatch Metrics landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('MetricsPage', ['LandingPage', 'CloudWatchCharts'])
    .controller('MetricsCtrl', function ($scope) {
        var vm = this;
        vm.initPage = function() {
        };
    })
;

