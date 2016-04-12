
angular.module('MetricGraphPage', ['CloudWatchCharts'])
    .controller('MetricsCtrl', function ($scope, $timeout, eucaUnescapeJson, eucaHandleError, ModalService) {
        // parse graph pre-selection
        params = $.url().param();
        if (params.graph !== undefined) {
            // parse graph params
            $scope.graph = purl("?"+$.base64.decode(params.graph)).param();
            $scope.graph.dimensions = JSON.parse($scope.graph.dimensions);
            if ($scope.graph.stat !== undefined) {
                if ($scope.graph.duration !== undefined) {
                    $scope.$broadcast("cloudwatch:updateLargeGraphParams", $scope.graph.stat, parseInt($scope.graph.period), parseInt($scope.graph.duration));
                }
                else {
                    $scope.$broadcast("cloudwatch:updateLargeGraphParams", $scope.graph.stat, parseInt($scope.graph.period), undefined, new Date($scope.graph.startTime), new Date($scope.graph.endTime));
                }
            }
        }
    })
;
