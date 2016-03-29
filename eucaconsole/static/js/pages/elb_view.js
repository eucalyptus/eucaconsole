/**
 * @fileOverview ELB Detail Page JS (General tab)
 * @requires AngularJS
 *
 */

angular.module('ELBPage', ['EucaConsoleUtils', 'ELBListenerEditor', 'ELBSecurityPolicyEditor', 'TagEditorModule',
                           'CreateBucketDialog', 'ELBSecurityGroupRulesWarning'])
    .controller('ELBPageCtrl', function ($scope, $http, $timeout, eucaUnescapeJson, eucaHandleUnsavedChanges,
                                         eucaHandleError, eucaFixHiddenTooltips, eucaCheckELBSecurityGroupRules) {
        $scope.elbForm = undefined;
        $scope.listenerArray = [];
        $scope.securityGroups = [];  // Selected security group ids (e.g. ["sg-123456", ...])
        $scope.securityGroupNames = [];  // Selected security group names (e.g. ["sgroup-one", ...])
        $scope.securityGroupChoices = {};  // id/name mapping of security group choices (e.g. {"sg-123": 'foo', ...})
        $scope.securityGroupCollection = [];  // Security group object choices
        $scope.selectedSecurityGroups = [];  // Selected security group objects
        $scope.loadBalancerInboundPorts = [];
        $scope.loadBalancerOutboundPorts = [];
        $scope.pingPort = '';
        $scope.certificateARN = '';
        $scope.certificateName = '';
        $scope.newCertificateName = '';
        $scope.privateKey = '';
        $scope.publicKeyCertificate = '';
        $scope.certificateChain = '';
        $scope.tempListenerBlock = {};
        $scope.showsCertificateTabDiv = false;
        $scope.backendCertificateArray = [];
        $scope.backendCertificateName = '';
        $scope.backendCertificateBody = '';
        $scope.backendCertificateTextarea = '';
        $scope.isBackendCertificateNotComplete = true;
        $scope.hasDuplicatedBackendCertificate = false;
        $scope.classDuplicatedBackendCertificateDiv = '';
        $scope.classAddBackendCertificateButton = 'disabled';
        $scope.classUseThisCertificateButton = 'disabled';
        $scope.vpcNetwork = 'None';
        $scope.isNotChanged = true;
        $scope.isInitComplete = false;
        $scope.loggingEnabled = false;
        $scope.bucketName = '';
        $scope.bucketNameField = $('#bucket_name');
        $scope.bucketNameChoices = {};
        $scope.accessLoggingConfirmed = false;
        $scope.accessLogConfirmationDialog = $('#elb-bucket-access-log-dialog');
        $scope.accessLogConfirmationDialogKey = 'doNotShowAccessLogConfirmationAgain';
        $scope.unsavedChangesWarningModalLeaveCallback = null;
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues(options);
            $scope.setWatch();
            $timeout(function(){
                $scope.isInitComplete = true;
            }, 1000);
        };
        $scope.setInitialValues = function (options) {
            var certArnField = $('#certificate_arn');
            var elbForm = $('#elb-form');
            if (elbForm.length > 0) {
                $scope.elbForm = elbForm;
            }
            $scope.securityGroupJsonEndpoint = options.securitygroups_json_endpoint;
            $scope.pingPort = options.ping_port;
            $scope.bucketName = $scope.bucketNameField.val();
            $scope.bucketNameChoices = options.bucket_choices;
            $scope.loggingEnabled = options.logging_enabled;
            $scope.existingCertificateChoices = options.existing_certificate_choices;
            if (options.securitygroups instanceof Array && options.securitygroups.length > 0) {
                $scope.securityGroups = options.securitygroups;
                // Timeout is needed for chosen to react after Angular updates the options
                $timeout(function(){
                    $('#securitygroup').trigger('chosen:updated');
                }, 500);
            }
            if (options.elb_vpc_network !== null) {
                $scope.vpcNetwork = options.elb_vpc_network;
                // Timeout is needed for the instance selector to be initizalized
                $timeout(function () {
                    $scope.$broadcast('eventWizardUpdateVPCNetwork', $scope.vpcNetwork);
                }, 500);
            }
            $scope.showsCertificateTabDiv = false;
            $scope.certificateTab = 'SSL';
            $scope.certificateRadioButton = 'existing';
            $scope.backendCertificateArray = [];
            if ($('#hidden_backend_certificates').length > 0) {
                $scope.backendCertificateTextarea = $('#hidden_backend_certificates');
            }
            $scope.isBackendCertificateNotComplete = true;
            $scope.hasDuplicatedBackendCertificate = false;
            $scope.classDuplicatedBackendCertificateDiv = '';
            $scope.classAddBackendCertificateButton = 'disabled';
            $scope.classUseThisCertificateButton = 'disabled';
            if (certArnField.children('option').length > 0) {
                $scope.certificateName = certArnField.children('option').first().text();
                $scope.certificateARN = certArnField.children('option').first().val();
            }
            $scope.initChosenSelectors();
        };
        $scope.initChosenSelectors = function () {
            $('#securitygroup').chosen({'width': '70%', search_contains: true});
        };
        $scope.getAllSecurityGroups = function (vpc) {
            if (!vpc || vpc === 'None') {
                return;
            }
            var csrf_token = $('#csrf_token').val();
            var data = "csrf_token=" + csrf_token + "&vpc_id=" + vpc;
            $http({
                method:'POST', url:$scope.securityGroupJsonEndpoint, data:data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.securityGroupCollection = results;
                results.forEach(function (sGroup){
                    $scope.securityGroupChoices[sGroup.id] = sGroup.name;
                });
            }).error(function (oData) {
                eucaHandleError(oData, status);
            });
        };
        $scope.setWatch = function () {
            eucaHandleUnsavedChanges($scope);
            eucaFixHiddenTooltips();
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');
                $(this).find('.dialog-progress-display').css('display', 'block');
            });
            $(document).on('click', '#security-policy-dialog-submit-btn', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $scope.$watch('loggingEnabled', function (newVal, oldVal) {
               // The Access Logs bucket name field is required only if logging is enabled
                var bucketNameField = $('#bucket_name');
                if (newVal) {
                    bucketNameField.attr('required', 'required');
                } else {
                    bucketNameField.removeAttr('required');
                }
                // Open Access Logs confirmation dialog when appropriate
                if (newVal !== oldVal) {
                    $scope.isNotChanged = false;
                    if (newVal) {
                        if (Modernizr.localstorage && !localStorage.getItem($scope.accessLogConfirmationDialogKey)) {
                            $scope.accessLogConfirmationDialog.foundation('reveal', 'open');
                        }
                    }
                }
            });
            $scope.accessLogConfirmationDialog.on('opened.fndtn.reveal', function () {
                $scope.accessLoggingConfirmed = false;
                $scope.$apply();
            });
            $scope.accessLogConfirmationDialog.on('close.fndtn.reveal', function () {
                if (!$scope.accessLoggingConfirmed) {
                    $scope.loggingEnabled = false;
                    $scope.$apply();
                }
                $('#bucket_name').focus().closest('.columns').removeClass('error');
            });
            $scope.$watch('securityGroups', function () {
                if ($scope.isInitComplete === true) {
                    $scope.isNotChanged = false;
                }
            }, true);
            $scope.$watch('vpcNetwork', function () {
                $scope.getAllSecurityGroups($scope.vpcNetwork);
            });
            $scope.$on('eventUpdateListenerArray', function ($event, listenerArray) {
                if ($scope.isInitComplete === true) {
                    $scope.isNotChanged = false;
                }
                $scope.listenerArray = listenerArray;
            });
            $scope.$on('eventOpenSelectCertificateModal', function ($event, fromProtocol, toProtocol, fromPort, toPort,
                                                                    certificateTab, existingCertId) {
                if ((fromProtocol === 'HTTPS' || fromProtocol === 'SSL') &&
                    (toProtocol === 'HTTPS' || toProtocol === 'SSL')) {
                    $scope.showsCertificateTabDiv = true;
                } else {
                    $scope.showsCertificateTabDiv = false;
                }
                $scope.tempListenerBlock = {
                    'fromProtocol': fromProtocol,
                    'fromPort': fromPort,
                    'toProtocol': toProtocol,
                    'toPort': toPort
                };
                $scope.certificateTab = certificateTab;
                $scope.openSelectCertificateModal(existingCertId);
            });
            $scope.$watch('certificateTab', function () {
                $scope.adjustSelectCertificateModalTabDisplay();
                $scope.setClassUseThisCertificateButton();
            });
            $scope.$watch('certificateARN', function(){
                var certArnField = $('#certificate_arn');
                var hiddenArnInput = $('#hidden_certificate_arn_input');
                // Find the certficate name when selected on the select certificate dialog
                if (certArnField.find('option:selected').length > 0) {
                    $scope.certificateName = certArnField.find('option:selected').text();
                }
                // Assign the certificate ARN value as hidden input
                if (hiddenArnInput.length > 0) {
                    hiddenArnInput.val($scope.certificateARN);
                }
                $scope.setClassUseThisCertificateButton();
                $scope.$broadcast('eventUpdateCertificateARN', $scope.certificateARN, $scope.tempListenerBlock);
            });
            $scope.$watch('certificateName', function(){
                // Broadcast the certificate name change to the elb listener directive
                $scope.$broadcast('eventUpdateCertificateName', $scope.certificateName);
            });
            $scope.$watch('certificateRadioButton', function () {
                $scope.setClassUseThisCertificateButton();
            });
            $scope.$watch('newCertificateName', function(){
                $scope.setClassUseThisCertificateButton();
            });
            $scope.$watch('privateKey', function(){
                $scope.setClassUseThisCertificateButton();
            });
            $scope.$watch('publicKeyCertificate', function(){
                $scope.setClassUseThisCertificateButton();
            });
            $scope.$watch('backendCertificateName', function () {
                $scope.checkAddBackendCertificateButtonCondition();
            });
            $scope.$watch('backendCertificateBody', function () {
                $scope.checkAddBackendCertificateButtonCondition();
            });
            $scope.$watch('backendCertificateArray', function () {
                $scope.syncBackendCertificates();
                $scope.checkAddBackendCertificateButtonCondition();
                $scope.setClassUseThisCertificateButton();
            }, true);
            $scope.$watch('isBackendCertificateNotComplete', function () {
                $scope.setClassAddBackendCertificateButton();
            });
            $scope.$watch('hasDuplicatedBackendCertificate', function () {
                $scope.setClassAddBackendCertificateButton();
                $scope.classDuplicatedBackendCertificateDiv = '';
                // timeout is needed for the DOM update to complete
                $timeout(function () {
                    if ($scope.hasDuplicatedBackendCertificate === true) {
                        $scope.classDuplicatedBackendCertificateDiv = 'error';
                    }
                });
            });
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $(document).on('input', 'input', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $(document).on('change', 'select', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
        };
        $scope.openModalById = function (modalID) {
            var modal = $('#' + modalID);
            modal.foundation('reveal', 'open');
            modal.find('h3').click();  // Workaround for dropdown menu not closing
        };
        $scope.openSelectCertificateModal = function (existingCertId) {
            var modal = $('#select-certificate-modal');
            var certArnField = $('#certificate_arn');
            if (modal.length > 0) {
                modal.foundation('reveal', 'open');
                $scope.certificateRadioButton = 'existing';
                $('#certificate-type-radio-existing').prop('checked', true);
                angular.forEach($scope.listenerArray, function (block) {
                    if (block.fromPort === $scope.tempListenerBlock.fromPort &&
                        block.toPort === $scope.tempListenerBlock.toPort) {
                        $scope.certificateARN = block.certificateARN;
                        $scope.certificateName = block.certificateName;
                    }
                });
                // Set Certificate ARN field to existing SSL cert ID if opened via "Change" link in listener editor
                if (!!existingCertId) {
                    $scope.certificateARN = (certArnField.find('option[value$="' + existingCertId + '"]').val());
                }
                // Remove any empty options created by Angular model issue
                certArnField.find('option').each(function () {
                    if ($(this).text() === '') {
                        $(this).remove();
                    }
                });
            }
        };
        $scope.selectCertificateTab = function ($event, tab) {
            $event.preventDefault();
            $scope.certificateTab = tab;
        };
        $scope.adjustSelectCertificateModalTabDisplay = function () {
            var sslTab = $('#select-certificate-modal-tab-ssl');
            var backendTab = $('#select-certificate-modal-tab-backend');
            sslTab.removeClass('active');
            backendTab.removeClass('active');
            if ($scope.certificateTab === 'SSL') {
                sslTab.addClass('active');
            } else {
                backendTab.addClass('active');
            }
        };
        $scope.createBackendCertificateArrayBlock = function () {
            return {
                'name': $scope.backendCertificateName,
                'certificateBody': $scope.backendCertificateBody
            };
        };
        $scope.addBackendCertificate = function ($event) {
            $event.preventDefault();
            $scope.checkAddBackendCertificateButtonCondition();
            // timeout is needed for all DOM updates and validations to be complete
            $timeout(function () {
                if( $scope.isBackendCertificateNotComplete === true || $scope.hasDuplicatedBackendCertificate === true){
                    return false;
                }
                // Add the backend certificate
                $scope.backendCertificateArray.push($scope.createBackendCertificateArrayBlock());
                $scope.$emit('backendCertificateArrayUpdate');
                $scope.resetBackendCertificateValues();
            });
        };
        $scope.syncBackendCertificates = function () {
            if ($scope.backendCertificateTextarea.length > 0) {
                var backendCertificateJSON = JSON.stringify($scope.backendCertificateArray);
                $scope.backendCertificateTextarea.val(backendCertificateJSON);
            }
        };
        $scope.resetBackendCertificateValues = function () {
            // Remove the required attr from the body field to avoid false negative validation error
            // when the input fields are cleared
            $('#backend_certificate_body').removeAttr('required');
            $scope.backendCertificateName = '';
            $scope.backendCertificateBody = '';
            // timeout is needed for Foundation's validation to complete
            // re-insert the required attr to the input field
            $timeout(function () {
                $('#backend_certificate_body').attr('required', 'required');
            }, 1000);
        };
        $scope.removeBackendCertificate = function ($event, index) {
            $event.preventDefault();
            $scope.backendCertificateArray.splice(index, 1);
        };
        $scope.setClassAddBackendCertificateButton = function () {
            if ($scope.isBackendCertificateNotComplete === true || $scope.hasDuplicatedBackendCertificate === true) {
                $scope.classAddBackendCertificateButton = 'disabled';
            } else {
                $scope.classAddBackendCertificateButton = '';
            }
        };
        $scope.setClassUseThisCertificateButton = function () {
            if ($scope.certificateTab === 'SSL') {
                if ($scope.certificateRadioButton === 'existing') {
                    if (!$scope.certificateARN) {
                        $scope.classUseThisCertificateButton = 'disabled';
                    } else {
                        $scope.classUseThisCertificateButton = '';
                    }
                } else {
                    if ($scope.newCertificateName === undefined || $scope.newCertificateName === '') {
                        $scope.classUseThisCertificateButton = 'disabled';
                    } else if ($scope.privateKey === undefined || $scope.privateKey === '') {
                        $scope.classUseThisCertificateButton = 'disabled';
                    } else if ($scope.publicKeyCertificate === undefined || $scope.publicKeyCertificate === '') {
                        $scope.classUseThisCertificateButton = 'disabled';
                    } else {
                        $scope.classUseThisCertificateButton = '';
                    }
                }
            } else if ($scope.certificateTab === 'BACKEND') {
                if ($scope.backendCertificateArray.length === 0) {
                    $scope.classUseThisCertificateButton = 'disabled';
                } else {
                    $scope.classUseThisCertificateButton = '';
                }
            } else {
                $scope.classUseThisCertificateButton = 'disabled';
            }
        };
        $scope.checkAddBackendCertificateButtonCondition = function () {
            if ($scope.backendCertificateName === '' || $scope.backendCertificateName === undefined) {
                $scope.isBackendCertificateNotComplete = true;
            } else if ($scope.backendCertificateBody === '' || $scope.backendCertificateBody === undefined) {
                $scope.isBackendCertificateNotComplete = true;
            } else {
                $scope.isBackendCertificateNotComplete = false;
            }
            $scope.checkForDuplicatedBackendCertificate();
        };
        $scope.checkForDuplicatedBackendCertificate = function () {
            $scope.hasDuplicatedBackendCertificate = false;
            // Create a new array block based on the current user input on the panel
            var newBlock = $scope.createBackendCertificateArrayBlock();
            for( var i=0; i < $scope.backendCertificateArray.length; i++){
                // Compare the new array block with the existing ones
                if ($scope.compareBackendCertificates(newBlock, $scope.backendCertificateArray[i])) {
                    $scope.hasDuplicatedBackendCertificate = true;
                    return;
                }
            }
            return;
        };
        $scope.compareBackendCertificates = function (block1, block2) {
            return block1.name === block2.name;
        };
        $scope.handleCertificateCreate = function ($event, newCertURL) {
            $event.preventDefault();
            if ($scope.classUseThisCertificateButton === 'disabled') {
                return false;
            }
            if ($scope.certificateRadioButton === 'new') {
                $scope.createNewCertificate(newCertURL);
            }
            var modal = $('#select-certificate-modal');
            if (modal.length > 0) {
                modal.foundation('reveal', 'close');
                $scope.$broadcast('eventUseThisCertificate', $scope.certificateARN, $scope.certificateName);
            }
        };
        $scope.createNewCertificate = function (url) {
            var certForm = $('#select-certificate-form');
            var formData = certForm.serialize();
            $scope.certificateForm = certForm;
            $scope.certificateForm.trigger('validate');
            if (!$scope.certificateARN && !$scope.newCertificateName) {
                return false;
            }
            $http({
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                method: 'POST',
                url: url,
                data: formData
            }).success(function (oData) {
                Notify.success(oData.message);
                if (oData.id) {
                    var newARN = oData.id;
                    $('#certificate_arn').append($("<option></option>")
                        .attr("value", newARN)
                        .text($scope.newCertificateName));
                    $scope.certificateARN = newARN;
                    // timeout is needed for the select element to be updated with the new option
                    $timeout(function () {
                        $scope.certificateName = $scope.newCertificateName;
                        // inform elb listener editor about the new certificate
                        $scope.$broadcast('eventUseThisCertificate', newARN, $scope.newCertificateName);
                    });
                }
            }).error(function (oData) {
                eucaHandleError(oData, status);
            });
        };
        $scope.confirmEnableAccessLogs = function () {
            var modal = $('#elb-bucket-access-log-dialog');
            if (modal.find('#dont-show-again').is(':checked') && Modernizr.localstorage) {
                localStorage.setItem($scope.accessLogConfirmationDialogKey, true);
            }
            $scope.accessLoggingConfirmed = true;
            $scope.accessLogConfirmationDialog.foundation('reveal', 'close');
        };
        $scope.updateELB = function ($event, confirmed) {
            confirmed = confirmed || false;
            $event.preventDefault();
            if ($scope.checkRequiredInput() && $scope.checkSecurityGroupRules(confirmed)) {
                $scope.elbForm.submit();
            }
        };
        $scope.checkRequiredInput = function () {
            // Handle the unsaved listener issue
            if ($('#from-port-input').val() !== '') {
                $('#unsaved-listener-warn-modal').foundation('reveal', 'open');
                $scope.isNotValid = true;
                return false;
            }
            return true;
        };
        $scope.checkSecurityGroupRules = function (confirmed) {
            var modal = $('#elb-security-group-rules-warning-modal');
            var inboundOutboundPortChecksPass;
            if ($scope.vpcNetwork === 'None') {  // Bypass rules check on non-VPC clouds
                return true;
            }
            inboundOutboundPortChecksPass = eucaCheckELBSecurityGroupRules($scope);
            if (!confirmed && !inboundOutboundPortChecksPass) {
                modal.foundation('reveal', 'open');
                return false;
            } else {
                return true;
            }
        };
    })
;
