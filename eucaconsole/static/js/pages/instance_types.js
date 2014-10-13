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
                    // Slight timedelay to ensure angular DOM completes  
                    $timeout(function () {
                        scope.$emit('ngRepeatFinished');
                    });
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
        $scope.nameColumnClass = {};
        $scope.cpuSelected = {};
        $scope.memorySelected = {};
        $scope.diskSelected = {};
        $scope.updatedItemList = {};
        $scope.cpuInputError = {};
        $scope.memoryInputError = {};
        $scope.diskInputError = {};
        $scope.chosenCreateOptionText = '';
        $scope.chosenNoResultsText = '';
        $scope.itemsLoading = true;
        $scope.isNotChanged = true;
        $scope.jsonEndpoint = '';
        $scope.submitEndpoint = '';
        $scope.pageResource = '';
        $scope.initController = function (jsonItemsEndpoint, submitEndpoint) {
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.submitEndpoint = submitEndpoint;
            $scope.initValues();
            $scope.getItems();
            $scope.setWatch();
        };
        $scope.initValues = function () {
            // Init text values
            $scope.chosenCreateOptionText = $('#chosen-create-option-text').text();
            $scope.chosenNoResultsText = $('#chosen-no-results-text').text();
        };
        $scope.initChosenWidgets = function () {
            angular.forEach($scope.items, function(item){
                $scope.initChosen('#select-cpu-'+item.name.replace(".", "\\."),
                    function(term){
                        var chosen = this;
                        var new_index = $(chosen).get(0).form_field.length;
                        var new_value = Number(term);
                        // Must be integer, greater than 0
                        if (new_value <= 0 || new_value != parseInt(new_value)) {
                            $scope.cpuInputError[item.name] = true;
                            // Make the error message disappear in 2 sec
                            $timeout(function() {
                                $scope.cpuInputError[item.name] = false;
                                $scope.$apply();
                            }, 2000);
                        } else {
                            // Slight delay prior to the option update
                            $timeout(function() {
                                chosen.append_option({
                                    value: new_index,
                                    text: new_value 
                                });
                                $scope.cpuInputError[item.name] = false;
                            });
                        }
                        $scope.$apply();
                    })
            });
            angular.forEach($scope.items, function(item){
                $scope.initChosen('#select-memory-'+item.name.replace(".", "\\."),
                    function(term){
                        var chosen = this;
                        var new_index = $(chosen).get(0).form_field.length;
                        var new_value = Number(term);
                        // Must be .25 .5 or .75 in case of decimals
                        if (new_value <= 0 || new_value * 4 != parseInt(new_value * 4)) {
                            $scope.memoryInputError[item.name] = true;
                            // Make the error message disappear in 2 sec
                            $timeout(function() {
                                $scope.memoryInputError[item.name] = false;
                                $scope.$apply();
                            }, 2000);
                        } else {
                            // Slight delay prior to the option update
                            $timeout(function() {
                                chosen.append_option({
                                    value: new_index,
                                    text: new_value 
                                });
                                $scope.memoryInputError[item.name] = false;
                            });
                        }
                        $scope.$apply();
                    })
            });
            angular.forEach($scope.items, function(item){
                $scope.initChosen('#select-disk-' + item.name.replace(".", "\\."),
                    function(term){
                        var chosen = this;
                        var new_index = $(chosen).get(0).form_field.length;
                        var new_value = Number(term);
                        // Must be integer, greater than 0
                        if (new_value <= 0 || new_value != parseInt(new_value)) {
                            $scope.diskInputError[item.name] = true;
                            // Make the error message disappear in 2 sec
                            $timeout(function() {
                                $scope.diskInputError[item.name] = false;
                                $scope.$apply();
                            }, 2000);
                        } else {
                            // Slight delay prior to the option update
                            $timeout(function() {
                                chosen.append_option({
                                    value: new_index,
                                    text: new_value 
                                });
                                $scope.diskInputError[item.name] = false;
                            });
                        }
                        $scope.$apply();
                    })
            });
        };
        $scope.initChosen = function(selector, createOptionCallback){
            $(selector).chosen({
                width: '80%', search_contains: true, 
                persistent_create_option: true,
                no_results_text: $scope.chosenNoResultsText, 
                create_with_enter: true,
                create_option_text: $scope.chosenCreateOptionText,
                create_option: createOptionCallback
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
            $scope.$watch('updatedItemList', function () {
                $scope.updateNameColumnClass();
            }, true); 
            $scope.$watch('cpuSelected', function () {
                if ($scope.checkForUpdatedCPUList() > 0) {
                    $scope.isNotChanged = false;
                }
            }, true);
            $scope.$watch('memorySelected', function () {
                if ($scope.checkForUpdatedMemoryList() > 0) {
                    $scope.isNotChanged = false;
                }
            }, true);
            $scope.$watch('diskSelected', function () {
                if ($scope.checkForUpdatedDiskList() > 0) {
                    $scope.isNotChanged = false;
                }
            }, true);
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
                    if (memory == $scope.convertMBtoGB(item.memory)) {
                        isDup = true;
                    }
                });
                if (!isDup ) {
                    $scope.memoryList.push($scope.convertMBtoGB(item.memory));
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
        $scope.checkForUpdatedCPUList = function () {
            var count = 0;
            angular.forEach($scope.items, function(item){
                if ($scope.cpuSelected[item.name] != item.cpu) {
                    $scope.updatedItemList[item.name] = true;
                    count++;
                } 
            });
            return count;
        };
        $scope.checkForUpdatedMemoryList = function () {
            var count = 0;
            angular.forEach($scope.items, function(item){
                if ($scope.memorySelected[item.name] != $scope.convertMBtoGB(item.memory)) {
                    $scope.updatedItemList[item.name] = true;
                    count++;
                } 
            });
            return count;
        };
        $scope.checkForUpdatedDiskList = function () {
            var count = 0;
            angular.forEach($scope.items, function(item){
                if ($scope.diskSelected[item.name] != item.disk) {
                    $scope.updatedItemList[item.name] = true;
                    count++;
                } 
            });
            return count;
        };
        $scope.checkForUpdatedItems = function () {
            var count = 0;
            count += $scope.checkForUpdatedCPUList();
            count += $scope.checkForUpdatedMemoryList();
            count += $scope.checkForUpdatedDiskList();
            return count;
        };
        $scope.buildUpdateObject = function () {
            var update = [];
            var selector = null;
            for (var key in $scope.updatedItemList) {
                var name = key;
                var cpu = $scope.cpuSelected[name];
                var memory = $scope.memorySelected[name];
                var disk = $scope.diskSelected[name];
                // Handle the cases where the input was typed rather than selected
                if (cpu == undefined) {
                    selector = '#select_cpu_' + name.replace(".", "_") + '_chosen';
                    cpu = $(selector).find('.chosen-single').text();
                }
                if (memory == undefined) {
                    selector = '#select_memory_' + name.replace(".", "_") + '_chosen';
                    memory = $(selector).find('.chosen-single').text();
                }
                if (disk == undefined) {
                    selector = '#select_disk_' + name.replace(".", "_") + '_chosen';
                    disk = $(selector).find('.chosen-single').text();
                }
                // Convert the memory unit back to MB
                memory = $scope.convertGBtoMB(memory);
                update.push({name: name, cpu: cpu, memory: memory, disk: disk}); 
            }
            return update;
        };
        $scope.submit = function($event) {
            if (!$scope.isNotChanged) {
                var form = $($event.target);
                var update = $scope.buildUpdateObject();
                var csrf_token = form.find('input[name="csrf_token"]').val();
                $http({method:'POST', url:$scope.submitEndpoint,
                       data: $.param({'csrf_token': csrf_token, update: update}),
                       headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                    success(function(oData) {
                        var results = oData ? oData.results : [];
                        Notify.success(oData.message);
                        $scope.submitCompleted();
                    }).error(function (oData, status) {
                        var errorMsg = oData['message'] || '';
                        if (errorMsg && status === 403) {
                            $('#timed-out-modal').foundation('reveal', 'open');
                        }
                        Notify.failure(errorMsg);
                    });
            } 
        };
        $scope.submitCompleted = function () {
            $scope.updatedItemList = {};
            $scope.nameColumnClass = {};
            $scope.isNotChanged = true;
            $scope.getItems();
        };
        $scope.updateNameColumnClass = function () {
            for (var key in $scope.updatedItemList) {
                $scope.nameColumnClass[key] = 'type-updated';
            }
        };
        $scope.convertMBtoGB = function (mb) {
            return Number(mb) / 1024;
        };
        $scope.convertGBtoMB = function (gb) {
            return Number(gb) * 1024;
        }
    })
;
