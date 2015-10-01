
angular.module('TemplateDesigner', ['EucaConsoleUtils'])
    .controller('TemplateDesignerCtrl', function($scope, $timeout, eucaUnescapeJson) {
        var vm = this;
        vm.initController = function(json_opts, blah) {
            /* html escape */
            json_opts = $('<div/>').html(json_opts).text();
            var opts = JSON.parse(eucaUnescapeJson(json_opts));
            vm.resources = opts.resources;
        };
    })
