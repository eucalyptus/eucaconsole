
angular.module('MetricGraphPage', ['CloudWatchCharts'])
    .controller('MetricsCtrl', function ($scope, $timeout, eucaUnescapeJson, eucaHandleError, ModalService) {
        // parse graph pre-selection
        params = $.url().param();
        if (params.graph !== undefined) {
            // parse graph params
            $scope.graph = purl("?"+$.base64.decode(params.graph)).param();
            graph.dimensions = JSON.parse(graph.dimensions);
            if (graph.stat !== undefined) {
                if (graph.duration !== undefined) {
                    $scope.$broadcast("cloudwatch:updateLargeGraphParams", graph.stat, parseInt(graph.period), parseInt(graph.duration));
                }
                else {
                    $scope.$broadcast("cloudwatch:updateLargeGraphParams", graph.stat, parseInt(graph.period), undefined, new Date(graph.startTime), new Date(graph.endTime));
                }
            }
        }
    })
;
