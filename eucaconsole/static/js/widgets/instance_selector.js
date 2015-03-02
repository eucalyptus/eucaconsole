/**
 * @fileOverview Instance Selector Directive JS
 * @requires AngularJS
 *
 */

eucaConsoleUtils.directive('instanceSelector', function() {
        return {
            restrict: 'E',
            scope: {
                option_json: '@options'
            },
            templateUrl: function (scope, elem) {
                return elem.template;
            },
            controller: function ($scope, $timeout, eucaHandleError, eucaUnescapeJson) {
                $scope.instanceList = [];
                $scope.instanceCount = 0;
		$scope.initSelector = function () {
		    var options = JSON.parse(eucaUnescapeJson($scope.option_json));
		    $scope.setInitialValues(options);
		    $scope.setWatcher();
		    $scope.setFocus();
		};
		$scope.setInitialValues = function (options) {
                    $scope.instanceCount = 0;
                    if (options.hasOwnProperty('protocol_list')) {
		        $scope.instanceList = options.instance_list;
                        if ($scope.instanceList instanceof Array && $scope.instanceList.length > 0) {
                            return;
                        }
                    }
		};
		$scope.setWatcher = function () {
		    $scope.$watch('instanceList', function(){
                        return;
		    }, true);
		};
		$scope.setFocus = function () {
                };
                $scope.initSelector();
            }
        };
    })
;
