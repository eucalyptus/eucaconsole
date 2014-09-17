/**
 * @fileOverview Instance Types page JS
 * @requires AngularJS
 *
 */

angular.module('InstanceTypesPage', [])
    .directive('onFinishRender', function ($timeout) {
        return {
            restrict: 'A',
            link: function (scope, element, attr) {
                if (scope.$last === true) {
                    $timeout(function () {
                        scope.$emit('ngRepeatFinished');
                    }, 1);
                }
            }
        }
    })
    .controller('InstanceTypesCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.cpuList = [];
        $scope.memoryList = [];
        $scope.diskList = [];
        $scope.cpuSelected = [];
        $scope.memorySelected = [];
        $scope.diskSelected = [];
        $scope.itemsLoading = true;
        $scope.jsonEndpoint = '';
        $scope.submitEndpoint = '';
        $scope.pageResource = '';
        $scope.initController = function (pageResource, jsonItemsEndpoint, submitEndpoint) {
            pageResource = pageResource || window.location.pathname.split('/')[0];
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.submitEndpoint = submitEndpoint;
            $scope.getItems();
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.initChosenWidgets = function () {
            angular.forEach($scope.items, function(item){
                $scope.initChosen('#select-cpu-'+item.name.replace(".", "\\."))
            });
            angular.forEach($scope.items, function(item){
                $scope.initChosen('#select-memory-'+item.name.replace(".", "\\."))
            });
            angular.forEach($scope.items, function(item){
                $scope.initChosen('#select-disk-'+item.name.replace(".", "\\."))
            });
        };
        $scope.initChosen = function(selector){
            $(selector).chosen({
                width: '80%', search_contains: true, create_option: function(term){
                    var chosen = this;
                    var new_value = term;
                    $timeout(function() {
                        chosen.append_option({
                            value: new_value,
                            text: new_value 
                        });
                    });
                },
                create_option_text: 'Insert a new value',
            });
        }; 
        $scope.setWatch = function () {
            $scope.$on('itemsLoaded', function () {
                $scope.getCPUList();
                $scope.getMemoryList();
                $scope.getDiskList();
            });
            $scope.$on('ngRepeatFinished', function () {
                $scope.initChosenWidgets();
            });
        };
        $scope.setFocus = function () {
        };
        $scope.getItems = function () {
            var csrf_token = $('#csrf_token').val();
            var data = "csrf_token="+csrf_token;
            $http({method:'POST', url:$scope.jsonEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.$emit('itemsLoaded', $scope.items);
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg) {
                    if (status === 403 || status === 400) {  // S3 token expiration responses return a 400
                        $('#timed-out-modal').foundation('reveal', 'open');
                    } else {
                        Notify.failure(errorMsg);
                    }
                }
            });
        };
        $scope.getCPUList = function () {
            angular.forEach($scope.items, function(item){
                var isDup = false;
                angular.forEach($scope.cpuList, function(cpu){
                    if (cpu == item.cpu) {
                        isDup = true;
                    }
                });
                if (!isDup ) {
                    $scope.cpuList.push(item.cpu);
                }
            });
            $scope.cpuList.sort(function(a,b){
                return a - b;
            });
        };
        $scope.getMemoryList = function () {
            angular.forEach($scope.items, function(item){
                var isDup = false;
                angular.forEach($scope.memoryList, function(memory){
                    if (memory == item.memory) {
                        isDup = true;
                    }
                });
                if (!isDup ) {
                    $scope.memoryList.push(item.memory);
                }
            });
            $scope.memoryList.sort(function(a,b){
                return a - b;
            });
        };
        $scope.getDiskList = function () {
            angular.forEach($scope.items, function(item){
                var isDup = false;
                angular.forEach($scope.diskList, function(disk){
                    if (disk == item.disk) {
                        isDup = true;
                    }
                });
                if (!isDup ) {
                    $scope.diskList.push(item.disk);
                }
            });
            $scope.diskList.sort(function(a,b){
                return a - b;
            });
        };
        $scope.submit = function($event) {
            var form = $($event.target);
            var data = form.serialize();
            console.log(data);
            $http({method:'POST', url:$scope.submitEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                Notify.success(oData.message);
                $scope.getItems();
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || '';
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                Notify.failure(errorMsg);
            });
        };
    })
;
