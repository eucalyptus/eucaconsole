/**
 * @fileOverview Stack Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('StackPage', ['EucaConsoleUtils'])
    .controller('StackPageCtrl', function ($scope, $http, eucaUnescapeJson) {
        $scope.stackStatusEndpoint = '';
        $scope.transitionalStates = ['create-in-progress', 'rollback-in-progress', 'delete-in-progress'];
        $scope.stackStatus = '';
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.stack_name = optionsJson.stack_name;
            $scope.stackStatusEndpoint = options.stack_status_json_url;
            if ($scope.stackStatusEndpoint) {
                $scope.getStackState();
            }
            //$scope.setWatch();
            $scope.setFocus();
        };
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.toggleTab = function (tab) {
            $(".tabs").children("dd").each(function() {
                var id = $(this).find("a").attr("href").substring(1);
                var $container = $("#" + id);
                $(this).removeClass("active");
                $container.removeClass("active");
                if (id == tab || $container.find("#" + tab).length) {
                    $(this).addClass("active");
                    $container.addClass("active");
                    $scope.currentTab = id; // Update the currentTab value for the help display
                    $scope.$broadcast('updatedTab', $scope.currentTab);
                }
             });
        };
        $scope.clickTab = function ($event, tab){
            $event.preventDefault();
            // If there exists unsaved changes, open the wanring modal instead
            if ($scope.isNotChanged === false) {
                $scope.openModalById('unsaved-changes-warning-modal');
                $scope.unsavedChangesWarningModalLeaveCallback = function() {
                    $scope.isNotChanged = true;
                    $scope.toggleTab(tab);
                    $('#unsaved-changes-warning-modal').foundation('reveal', 'close');
                };
                return;
            } 
            $scope.toggleTab(tab);
        };
        $scope.setWatch = function () {
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.actions-menu').find('a').get(0).focus();
            });
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if (modalID.match(/delete/)) {
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                } else {
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement) {
                        inputElement.focus();
                    } else {
                        if (!!modalButton) {
                            modalButton.focus();
                        }
                    }
                }
            });
        };
        $scope.getStackState = function () {
            $http.get($scope.stackStatusEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.stackStatus = results.stack_status;
                    $scope.outputs = results.outputs;
                    $scope.resources = results.resources;
                    // Poll to obtain desired end state if current state is transitional
                    if ($scope.isTransitional($scope.stackStatus)) {
                        $scope.isUpdating = true;
                        $timeout(function() {$scope.getStackState();}, 4000);  // Poll every 4 seconds
                    } else {
                        $scope.isUpdating = false;
                    }
                }
            });
        };
    })
;

