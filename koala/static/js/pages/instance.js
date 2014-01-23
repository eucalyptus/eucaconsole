/**
 * @fileOverview Instance page JS
 * @requires AngularJS
 *
 */

// Instance page includes the tag editor, so pull in that module as well.
angular.module('InstancePage', ['TagEditor'])
    .controller('InstancePageCtrl', function ($scope, $http, $timeout) {
        $scope.instanceStateEndpoint = '';
        // Valid instance states are: "pending", "running", "shutting-down", "terminated", "stopping", "stopped"
        // 'shutting-down' = terminating state
        $scope.transitionalStates = ['pending', 'stopping', 'shutting-down'];
        $scope.instanceState = '';
        $scope.isUpdating = false;
        $scope.isNotStopped = $scope.instanceState != 'stopped';
        $scope.instanceForm = $('#instance-form');
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.initController = function (jsonEndpoint, consoleEndpoint, state) {
            $scope.instanceStateEndpoint = jsonEndpoint;
            $scope.consoleOutputEndpoint = consoleEndpoint;
            $scope.instanceState = state;
            $scope.getInstanceState();
        };
        $scope.revealConsoleOutputModal = function() {
            $http.get($scope.consoleOutputEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.consoleOutput = results;
                    var modal = $('#console-output-modal');
                    modal.foundation('reveal', 'open');
                }
            });
        };
        $scope.getInstanceState = function () {
            $http.get($scope.instanceStateEndpoint).success(function(oData) {
                $scope.instanceState = oData ? oData.results : '';

                // Poll to obtain desired end state if current state is transitional
                if ($scope.isTransitional($scope.instanceState)) {
                    $scope.isUpdating = true;
                    $timeout(function() {$scope.getInstanceState()}, 4000);  // Poll every 4 seconds
                } else {
                    $scope.isUpdating = false;
                }
                $scope.isNotStopped = $scope.instanceState != 'stopped';
            });
        };
        $scope.submitUpdateInstance = function ($event) {
            $event.preventDefault();
            $('a.close-reveal-modal').trigger('click');
            $('#start_later').val('true');
            $scope.instanceForm.submit();
        };
        $scope.cancelUpdateInstance = function ($event) {
            $event.preventDefault();
            $('a.close-reveal-modal').trigger('click');
            $scope.instanceForm.submit();
        };
    })
;

