/**
 * @fileOverview ELB Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('ELBPage', ['EucaConsoleUtils', 'ELBListenerEditor', 'TagEditor'])
    .controller('ELBPageCtrl', function ($scope, $timeout, eucaUnescapeJson) {
        $scope.isNotChanged = true;
        $scope.securityGroups = [];
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues(options);
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.setInitialValues = function (options) {
            if (options.hasOwnProperty('securitygroups')) {
                if (options.securitygroups instanceof Array && options.securitygroups.length > 0) {
                    $scope.securityGroups = options.securitygroups;
                    // Timeout is needed for chosen to react after Angular updates the options
                    $timeout(function(){
                        $('#securitygroup').trigger('chosen:updated');
                    }, 500);
                }
            }
            if (options.hasOwnProperty('in_use')) {
                $scope.elbInUse = options.in_use;
            }
            if (options.hasOwnProperty('has_image')) {
                $scope.hasImage = options.has_image;
            }
            if (!$scope.hasImage) {
                $('#image-missing-modal').foundation('reveal', 'open');
            }
            $scope.initChosenSelectors(); 
        };
        $scope.initChosenSelectors = function () {
            $('#securitygroup').chosen({'width': '100%', search_contains: true});
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
            $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if( modalID.match(/terminate/)  || modalID.match(/delete/) || modalID.match(/release/) ){
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                }else{
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement) {
                        inputElement.focus();
                    } else if (!!modalButton) {
                        modalButton.focus();
                    }
               }
            });
        };
        $scope.submitSaveChanges = function ($event) {
        };
    })
;



