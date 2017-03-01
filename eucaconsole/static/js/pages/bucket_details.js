/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Bucket detail page JS
 * @requires AngularJS, jQuery
 *
 */

/* Bucket details page includes the S3 Sharing Panel */
angular.module('BucketDetailsPage',
    ['S3SharingPanel', 'EucaConsoleUtils', 'CorsServiceModule', 'BucketPolicyServiceModule', 'TagEditorModule', 'ModalModule'])
    .controller('BucketDetailsPageCtrl', function ($scope, $rootScope, $http, eucaHandleErrorS3,
                                                   eucaUnescapeJson, CorsService, BucketPolicyService) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.bucketName = '';
        $scope.bucketDetailsForm = $('#bucket-details-form');
        $scope.isSubmitted = false;
        $scope.hasChangesToBeSaved = false;
        $scope.objectsCountLoading = true;
        $scope.savingCorsConfig = false;
        $scope.deletingCorsConfig = false;
        $scope.corsConfigXml = '';
        $scope.hasCorsConfig = false;
        $scope.hasBucketPolicy = false;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.bucketName = options.bucket_name;
            $scope.bucketObjectsCountUrl = options.bucket_objects_count_url;
            $scope.corsConfigXml = options.cors_config_xml;
            $scope.bucketPolicyJson = options.bucket_policy_json;
            $scope.hasCorsConfig = !!$scope.corsConfigXml;
            $scope.hasBucketPolicy = !!$scope.bucketPolicyJson;
            $scope.initPolicyDialogListener();
            $scope.getBucketObjectsCount();
            $scope.handleUnsavedChanges();
            $scope.handleUnsavedSharingEntry($scope.bucketDetailsForm);
            // set upload button target based on media query
            if (Foundation.utils.is_medium_up()) {
                $('#upload-file-action').attr('target', 'upload-file');
            }
        };
        $scope.getBucketObjectsCount = function () {
            $http.get($scope.bucketObjectsCountUrl).success(function(oData) {
                var results = oData ? oData.results : {};
                $scope.bucketCount = results.object_count;
                $scope.versionCount = results.version_count;
                $scope.objectsCountLoading = false;
            }).error(function (oData, status) {
                eucaHandleErrorS3(oData, status);
            });
        };
        $scope.initPolicyDialogListener = function () {
            var policyDialog = $('#bucket-policy-modal');
            policyDialog.on('opened.fndtn.reveal', function () {
                var policyTextarea = document.getElementById('policy-textarea');
                policyDialog.find('.CodeMirror').remove();  // Avoid duplicate CodeMirror textareas
                if (policyTextarea !== null) {
                    $scope.policyCodeEditor = CodeMirror.fromTextArea(policyTextarea, {
                        mode: "javascript",
                        lineWrapping: true,
                        styleActiveLine: true,
                        lineNumbers: true
                    });
                }
            });
        };
        $scope.setBucketPolicy = function ($event) {
            $event.preventDefault();
            $scope.savingBucketPolicy = true;
            $scope.policyError = '';
            var csrfToken = angular.element('#csrf_token').val();
            var policyTextarea = angular.element('#policy-textarea');
            // Fall back to standard textarea in cases where CodeMirror fails to initialize
            var policyValue = $scope.policyCodeEditor && $scope.policyCodeEditor.getValue() || policyTextarea.val();
            BucketPolicyService.setBucketPolicy($scope.bucketName, csrfToken, policyValue)
                .then(function success(response) {
                    $scope.savingBucketPolicy = false;
                    $rootScope.$broadcast('s3:bucketPolicySaved');
                    $('#bucket-policy-modal').foundation('reveal', 'close');
                    Notify.success(response.data.message);
                }, function error(errData) {
                    $scope.policyError = errData.data.message;
                    $scope.savingBucketPolicy = false;
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
        $scope.revealModal = function (action) {
            var modal = $('#' + action + '-modal');
            modal.foundation('reveal', 'open');
            modal.find('h3').click();  // Workaround for dropdown menu not closing
        };
        $scope.handleUnsavedChanges = function () {
            // Listen for sharing panel update
            $scope.$on('s3:sharingPanelAclUpdated', function () {
                $scope.hasChangesToBeSaved = true;
            });
            // Listen for metadata update
            $scope.$on('s3:objectMetadataUpdated', function () {
                $scope.hasChangesToBeSaved = true;
            });
            $scope.$watch('objectName', function (newVal, oldVal) {
                if (newVal !== oldVal) {
                    $scope.hasChangesToBeSaved = true;
                }
            });
            //
            $('#propagate_acls').on('change', function () {
                if ($(this).is(':checked')) {
                    $scope.hasChangesToBeSaved = true;
                }
            });
            $scope.$on('tagUpdate', function($event) {
                $scope.hasChangesToBeSaved = true;
            });
            // Turn "isSubmitted" flag to true when a form (except the logout form) is submitted
            $('form[id!="euca-logout-form"]').on('submit', function () {
                $scope.isSubmitted = true;
            });
            // Warn the user about the unsaved changes
            window.onbeforeunload = function() {
                if ($scope.hasChangesToBeSaved && !$scope.isSubmitted) {
                    return $('#warning-message-unsaved-changes').text();
                }
            };
        };
        $scope.handleUnsavedSharingEntry = function (form) {
            // Display warning when there's an unsaved Sharing Panel entry
            form.on('submit', function (event) {
                var accountInputField = form.find('#share_account:visible');
                if (accountInputField.length && accountInputField.val() !== '') {
                    event.preventDefault();
                    $scope.isSubmitted = false;
                    $('#unsaved-sharing-warning-modal').foundation('reveal', 'open');
                    return false;
                }
            });
        };
        $scope.deleteCorsConfig = function ($event) {
            $event.preventDefault();
            $scope.deleteError = '';
            $scope.deletingCorsConfig = true;
            var deleteDialog = $('#cors-delete-confirmation-modal');
            var csrfToken = angular.element('#csrf_token').val();
            CorsService.deleteCorsConfig($scope.bucketName, csrfToken)
                .then(function success (response) {
                    deleteDialog.foundation('reveal', 'close');
                    $scope.deletingCorsConfig = false;
                    $scope.hasCorsConfig = false;
                    Notify.success(response.data.message);
                }, function error (errData) {
                    $scope.deleteError = errData.data.message;
                    $scope.deletingCorsConfig = false;
                });
        };
        $rootScope.$on('s3:corsConfigSaved', function () {
            $scope.hasCorsConfig = true;
        });
        // Receive postMessage from file upload window, refreshing list when file upload completes
        window.addEventListener('message', function (event) {
            if (event.data === 's3:fileUploaded') {
                $scope.getBucketObjectsCount();
            }
        }, false);
    })
    .directive('corsConfigModal', function() {
        return {
            restrict: 'A',
            scope: {
                template: '@',
                bucketName: '@',
                hasCorsConfig: '=',
                corsConfigXml: '@',
                sampleCorsConfig: '@'
            },
            templateUrl: function (element, attributes) {
                return attributes.template;
            },
            controller: ['$scope', '$rootScope', 'CorsService', 'ModalService',
                function($scope, $rootScope, CorsService, ModalService) {
                    if (!$scope.hasCorsConfig) {
                        $scope.corsConfigXml = $scope.sampleCorsConfig;
                    }
                    $scope.setCorsConfiguration = function ($event) {
                        $event.preventDefault();
                        $scope.savingCorsConfig = true;
                        $scope.corsError = '';
                        var csrfToken = angular.element('#csrf_token').val();
                        var corsTextarea = angular.element('#cors-textarea');
                        // Fall back to standard textarea in cases where CodeMirror fails to initialize
                        var corsConfigValue = $scope.codeEditor && $scope.codeEditor.getValue() || corsTextarea.val();
                        CorsService.setCorsConfig($scope.bucketName, csrfToken, corsConfigValue)
                            .then(function success (response) {
                                $scope.savingCorsConfig = false;
                                $rootScope.$broadcast('s3:corsConfigSaved');
                                ModalService.closeModal('corsConfigModal');
                                Notify.success(response.data.message);
                            }, function error (errData) {
                                $scope.corsError = errData.data.message;
                                $scope.savingCorsConfig = false;
                            });
                    };
                    // FIXME: modal:open doesn't fire in Angular 1.5
                    $scope.$on('modal:open', function ($event, modalName) {
                        if (modalName === 'corsConfigModal') {
                            // Initialize CodeMirror for CORS XML textarea
                            var corsTextarea = document.getElementById('cors-textarea');
                            $('.CodeMirror').remove();  // Avoid duplicate CodeMirror textareas
                            if (corsTextarea !== null) {
                                $scope.codeEditor = CodeMirror.fromTextArea(corsTextarea, {
                                    mode: "xml",
                                    lineWrapping: true,
                                    styleActiveLine: true,
                                    autoCloseTags: true,
                                    lineNumbers: true
                                });
                            }
                            // Reset to sample CORS config when re-adding post-deletion
                            if (!$scope.hasCorsConfig && !!$scope.codeEditor) {
                                 $scope.codeEditor.setValue($scope.sampleCorsConfig);
                            }
                        }
                    });
                }
            ]
        };
    })
;

