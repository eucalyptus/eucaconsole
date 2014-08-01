/**
 * @fileOverview Volume page JS
 * @requires AngularJS
 *
 */

// Volume page includes the tag editor, so pull in that module as well.
angular.module('VolumePage', ['TagEditor'])
    .controller('VolumePageCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.volumeStatusEndpoint = '';
        $scope.transitionalStates = ['creating', 'deleting', 'attaching', 'detaching'];
        $scope.volumeStatus = '';
        $scope.volumeAttachStatus = '';
        $scope.snapshotId = '';
        $scope.instanceId = '';
        $scope.isNotValid = true;
        $scope.isNotChanged = true;
        $scope.isSubmitted = false;
        $scope.isUpdating = false;
        $scope.fromSnapshot = false;
        $scope.volumeSize = 1;
        $scope.snapshotSize = 1;
        $scope.urlParams = $.url().param();
        $scope.initController = function (jsonEndpoint, status, attachStatus) {
            $scope.initChosenSelectors();
            $scope.volumeStatusEndpoint = jsonEndpoint;
            $scope.volumeStatus = status.replace('-', ' ');
            $scope.volumeAttachStatus = attachStatus;
            if (jsonEndpoint) {
                $scope.getVolumeState();
            }
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.populateVolumeSize = function () {
           if ($scope.snapshotId == '') {
                $scope.snapshotSize = 1;
                $scope.volumeSize = 1;
                return;
            }
            $http.get("/snapshots/"+$scope.snapshotId+"/size/json").success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.snapshotSize = results;
                    $scope.volumeSize = results;
                }
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
            });
        };
        $scope.initChosenSelectors = function () {
            var snapshotField = $('#snapshot_id');
            if ($scope.urlParams['from_snapshot']) {  // Pre-populate snapshot if passed in query string arg
                $scope.fromSnapshot = true;
                snapshotField.val($scope.urlParams['from_snapshot']);
                $scope.snapshotId = $scope.urlParams['from_snapshot'];
                $scope.populateVolumeSize();
            }
            snapshotField.chosen({'width': '75%', 'search_contains': true});
            // Instance choices in "Attach to instance" modal dialog
            $('#attach-volume-modal').on('open', function() {
                $('#instance_id').chosen({'width': '75%', search_contains: true});
            });
        };
        $scope.getVolumeState = function () {
            $http.get($scope.volumeStatusEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.volumeStatus = results['volume_status'];
                    $scope.volumeAttachStatus = results['attach_status'];
                    $scope.device_name = results['attach_device'];
                    $scope.attach_time = results['attach_time'];
                    $scope.attach_instance = results['attach_instance'];
                    // Poll to obtain desired end state if current state is transitional
                    if ($scope.isTransitional($scope.volumeStatus) || $scope.isTransitional($scope.volumeAttachStatus)) {
                        $scope.isUpdating = true;
                        $timeout(function() {$scope.getVolumeState()}, 4000);  // Poll every 4 seconds
                    } else {
                        $scope.isUpdating = false;
                    }
                }
            });
        };
        $scope.getDeviceSuggestion = function () {
            // TODO: the url shouldn't be built by hand, pass value from request.route_path!
            $http.get("/instances/"+$scope.instanceId+"/nextdevice/json").success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $('input#device').val(results);
                }
            });
        };
        // True if there exists an unsaved key or value in the tag editor field
        $scope.existsUnsavedTag = function () {
            var hasUnsavedTag = false;
            $('input.taginput[type!="checkbox"]').each(function(){
                if ($(this).val() !== '') {
                    hasUnsavedTag = true;
                }
            });
            return hasUnsavedTag;
        };
        $scope.setWatch = function () {
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $scope.$watch('volumeSize', function () {
                if ($scope.volumeSize < $scope.snapshotSize || $scope.volumeSize === undefined) {
                    $('#volume_size_error').removeClass('hide');
                    $scope.isNotValid = true;
                }else{
                    $('#volume_size_error').addClass('hide');
                    $scope.isNotValid = false;
                }
            });
            // Handle the unsaved tag issue
            $(document).on('submit', '#volume-detail-form', function(event) {
                $('input.taginput').each(function(){
                    if ($(this).val() !== '') {
                        event.preventDefault(); 
                        $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
                        return false;
                    }
                });
            });
            // Turn "isSubmiited" flag to true when a submit button is clicked on the page
            $('form[id!="euca-logout-form"]').on('submit', function () {
                $scope.isSubmitted = true;
            });
            window.onbeforeunload = function(event) {
                // Conditions to check before navigate away from the page
                // Either by "Submit" or clicking links on the page
                if ($scope.existsUnsavedTag()) {
                    // In case of any unsaved tags, warn the user before unloading the page
                    return $('#warning-message-unsaved-tag').text();
                } else if ($scope.isNotChanged === false) {
                    // No unsaved tags, but some input fields have been modified on the page
                    if ($scope.isSubmitted === true) {
                        // The action is "submit". OK to proceed
                        return;
                    } else {
                        // The action is navigate away.  Warn the user about the unsaved changes
                        return $('#warning-message-unsaved-change').text();
                    }
                }
            };
            // Do not perfom the unsaved changes check if the cancel link is clicked
            $(document).on('click', '.cancel-link', function(event) {
                window.onbeforeunload = null;
            });
            // Handle the case when user tries to open a dialog while there exist unsaved changes
            $(document).on('open', '[data-reveal][id!="unsaved-changes-warning-modal"][id!="unsaved-tag-warn-modal"]', function () {
                // If there exist unsaved changes
                if ($scope.existsUnsavedTag() || $scope.isNotChanged === false) {
                    var self = this;
                    // Close the current dialog as soon as it opens
                    $(self).on('opened', function() {
                        $(self).off('opened');
                        $(self).foundation('reveal', 'close');
                    });
                    // Open the warning message dialog instead
                    $(self).on('closed', function() {
                        $(self).off('closed');
                        var modal = $('#unsaved-changes-warning-modal');
                        modal.foundation('reveal', 'open');
                    });
                } 
            });
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
            $(document).on('input', 'input[type="text"]', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                var tabs = $('.tabs').find('a');
                if (tabs.length > 0) {
                    tabs.get(0).focus();
                } else if ($('input[type="text"]').length > 0) {
                    $('input[type="text"]').get(0).focus();
                }
            });
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if (modalID.match(/terminate/) || modalID.match(/delete/) || modalID.match(/release/)) {
                    var closeMark = modal.find('.close-reveal-modal');
                    if (!!closeMark) {
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
        $scope.detachModal = function (device_name, url) {
            var warnModal = $('#detach-volume-warn-modal'),
                detachModal = $('#detach-volume-modal');

            $http.get(url).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    if (results.root_device_name == device_name) {
                        warnModal.foundation('reveal', 'open');
                        warnModal.find('h3').click();  // Workaround for dropdown menu not closing
                    } else {
                        detachModal.foundation('reveal', 'open');
                        detachModal.find('h3').click();
                    }
                }
            });
        };
    })
;

