/**
 * @fileOverview Elastic Load Balancer Wizard JS
 * @requires AngularJS
 *
 */

angular.module('EucaConsoleWizard').controller('ELBWizardCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
    $scope.elbForm = undefined;
    $scope.urlParams = undefined;
    $scope.isNotValid = true;
    $scope.securityGroupJsonEndpoint = '';
    $scope.elbName = '';
    $scope.listenerArray = [];
    $scope.vpcNetwork = '';
    $scope.vpcNetworkName = '';
    $scope.vpcSubnets = [];
    $scope.vpcSubnetNames = [];
    $scope.vpcSubnetChoices = [];
    $scope.vpcSubnetList = [];
    $scope.securityGroups = [];
    $scope.securityGroupNames = [];
    $scope.securityGroupChoices = [];
    $scope.securityGroupCollection = []; 
    $scope.availabilityZones = [];
    $scope.instanceList = [];
    $scope.classNoInstanceWarningDiv = '';
    $scope.crossZoneEnabled = false;
    $scope.protocolList = []; 
    $scope.pingProtocol = '';
    $scope.pingPort = '';
    $scope.pingPath = '';
    $scope.responseTimeout = '';
    $scope.timeBetweenPings = '';
    $scope.failuresUntilUnhealthy = '';
    $scope.passesUntilUnhealthy = '';
    $scope.certificateTab = 'SSL';
    $scope.certificateRadioButton = '';
    $scope.certificateARN = '';
    $scope.certificateName = '';
    $scope.newCertificateName = '';
    $scope.showsCertificateTabDiv = false;
    $scope.backendCertificateArray = [];
    $scope.backendCertificateName = '';
    $scope.backendCertificateBody = '';
    $scope.backendCertificateTextarea = '';
    $scope.isBackendCertificateNotComplete = true;
    $scope.hasDuplicatedBackendCertificate = false;
    $scope.duplicatedBackendCertificateDivClass = '';
    $scope.addBackendCertificateButtonClass = 'disabled';
    $scope.initController = function (optionsJson) {
        var options = JSON.parse(eucaUnescapeJson(optionsJson));
        $scope.setInitialValues(options);
        $scope.setWatcher();
        $scope.setFocus();
    };
    $scope.setInitialValues = function (options) {
        $scope.elbForm = $('#elb-form');
        $scope.urlParams = $.url().param();
        $scope.isNotValid = true;
        $scope.securityGroupJsonEndpoint = options.securitygroups_json_endpoint;
        if (options.hasOwnProperty('protocol_list')) {
            $scope.protocolList = options.protocol_list;
            if ($scope.protocolList instanceof Array && $scope.protocolList.length > 0) {
                $scope.pingProtocol = $scope.protocolList[0].name;
            }
        }
        if (options.hasOwnProperty('default_vpc_network')) {
            $scope.vpcNetwork = options.default_vpc_network;
        }
        if (options.hasOwnProperty('vpc_subnet_choices')) {
            $scope.vpcSubnetList = options.vpc_subnet_choices;
            $scope.updateVPCSubnetChoices();
        }
        $scope.listenerArray = [];
        $scope.instanceList = [];
        $scope.crossZoneEnabled = false;
        $scope.pingProtocol = 'HTTP';
        $scope.pingPort = 80;
        $scope.pingPath = '/index.html';
        $scope.responseTimeout = 5;
        $scope.timeBetweenPings = 30;
        $scope.failuresUntilUnhealthy = 2;
        $scope.passesUntilUnhealthy = 10;
        $scope.showsCertificateTabDiv = false;
        $scope.certificateTab = 'SSL';
        $scope.certificateRadioButton = "existing";
        $scope.backendCertificateArray = [];
        if ($('#hidden_backend_certificates').length > 0) {
            $scope.backendCertificateTextarea = $('#hidden_backend_certificates');
        }
        $scope.isBackendCertificateNotComplete = true;
        $scope.hasDuplicatedBackendCertificate = false;
        $scope.duplicatedBackendCertificateDivClass = '';
        $scope.addBackendCertificateButtonClass = 'disabled';
        // timeout is needed to wait for the elb listener directive to be initialized
        if ($('#certificates').children('option').length > 0) {
            $scope.certificateName = $('#certificates').children('option').first().text();
            $scope.certificateARN = $('#certificates').children('option').first().val();
        }
        $scope.initChosenSelectors(); 
    };
    $scope.initChosenSelectors = function () {
        $('#vpc_subnet').chosen({'width': '100%', search_contains: true});
        $('#securitygroup').chosen({'width': '100%', search_contains: true});
        $('#zone').chosen({'width': '100%', search_contains: true});
    };
    $scope.setWatcher = function (){
        // Handle the next step tab click event
        $scope.$on('eventClickVisitNextStep', function($event, thisStep, nextStep) {
            $scope.checkRequiredInput(thisStep);
            // Signal the parent wizard controller about the completion of the next step click event
            $scope.$emit('eventProcessVisitNextStep', nextStep);
            $timeout(function() {
                // Workaround for the broken placeholer message issue
                // Wait until the rendering of the new tab page is complete
                $('#zone').trigger("chosen:updated");
                $('#vpc_subnet').trigger('chosen:updated');
            });
        });
        $scope.$on('currentStepIndexUpdate', function($event, thisStepIndex) {
            $scope.checkRequiredInput(thisStepIndex+1);
        });
        $scope.$on('eventUpdateListenerArray', function ($event, listenerArray) {
            $scope.listenerArray = listenerArray;
        });
        $scope.$on('eventOpenSelectCertificateModal', function ($event, fromProtocol, toProtocol, certificateTab) {
            if ((fromProtocol === 'HTTPS' || fromProtocol === 'SSL') &&
                (toProtocol === 'HTTPS' || toProtocol === 'SSL')) {
                $scope.showsCertificateTabDiv = true;
            } else {
                $scope.showsCertificateTabDiv = false;
            }
            $scope.certificateTab = certificateTab;
            $scope.openSelectCertificateModal();
        });
        $scope.$on('eventUpdateSelectedInstanceList', function ($event, instanceList) {
            $scope.instanceList = instanceList;
        });
        $scope.$watch('elbName', function (){
            $scope.checkRequiredInput(1);
        });
        $scope.$watch('vpcNetwork', function () {
            $scope.availabilityZones = [];
            $scope.vpcSubnets = [];
            $scope.securityGroups = [];
            $scope.updateVPCNetworkName();
            $scope.getAllSecurityGroups($scope.vpcNetwork);
            $scope.updateVPCSubnetChoices();
            $scope.checkRequiredInput(2);
        }, true);
        $scope.$watch('securityGroups', function () {
            $scope.updateSecurityGroupNames();
            $scope.checkRequiredInput(2);
        }, true);
        $scope.$watch('securityGroupCollection', function () {
            $scope.updateSecurityGroupChoices();
        }, true);
        $scope.$watch('availabilityZones', function () {
            $scope.checkRequiredInput(3);
            $scope.$broadcast('eventUpdateAvailabilityZones', $scope.availabilityZones);
        }, true);
        $scope.$watch('vpcSubnets', function () {
            $scope.updateVPCSubnetNames();
            $scope.checkRequiredInput(3);
            $scope.$broadcast('eventUpdateVPCSubnets', $scope.vpcSubnets);
        }, true);
        $scope.$watch('instanceList', function (newValue, oldValue) {
            $scope.checkRequiredInput(3);
            $scope.classNoInstanceWarningDiv = '';
            if (oldValue.length > 0 && $scope.instanceList.length === 0 ) {
                $scope.classNoInstanceWarningDiv = 'error';
            }
        }, true);
        $scope.$watch('pingProtocol', function (){
            $scope.updateDefaultPingProtocol();
        });
        $scope.$watch('pingPort', function (){
            $scope.checkRequiredInput(4);
        });
        $scope.$watch('responseTimeout', function (){
            $scope.checkRequiredInput(4);
        });
        $scope.$watch('certificateTab', function () {
            $scope.adjustSelectCertificateModalTabDisplay();
        });
        $scope.$watch('certificateARN', function(){
            // Find the certficate name when selected on the select certificate dialog
            if ($('#certificates option:selected').length > 0) {
                $scope.certificateName = $('#certificates option:selected').text();
            }
            // Assign the certificate ARN value as hidden input
            if ($('#hidden_certificate_arn_input').length > 0) {
                $('#hidden_certificate_arn_input').val($scope.certificateARN);
            }
        });
        $scope.$watch('certificateName', function(){
            // Broadcast the certificate name change to the elb listener directive
            $scope.$broadcast('eventUpdateCertificateName', $scope.certificateName);
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
        }, true);
        $scope.$watch('isBackendCertificateNotComplete', function () {
            $scope.setAddBackendCertificateButtonClass();
        });
        $scope.$watch('hasDuplicatedBackendCertificate', function () {
            $scope.setAddBackendCertificateButtonClass();
            $scope.duplicatedBackendCertificateDivClass = '';
            // timeout is needed for the DOM update to complete
            $timeout(function () {
                if ($scope.hasDuplicatedBackendCertificate === true) {
                    $scope.duplicatedBackendCertificateDivClass = 'error';
                }
            });
        });
        $scope.$on('searchUpdated', function ($event, query) {
            // Relay the query search update signal
            $scope.$broadcast('eventQuerySearch', query);
        });
        $scope.$on('textSearch', function ($event, searchVal, filterKeys) {
            // Relay the text search update signal
            $scope.$broadcast('eventTextSearch', searchVal, filterKeys);
        });
    };
    $scope.setFocus = function () {
    };
    $scope.checkRequiredInput = function (step) {
        $scope.isNotValid = false;
        if (step === 1) {
            var elbListenerTextArea = $('#elb-listener');
            if ($scope.elbName === '' || $scope.elbName === undefined) {
                $scope.isNotValid = true;
            } else if (elbListenerTextArea.length > 0) {
                if (elbListenerTextArea.val() === '' || elbListenerTextArea.val() === '[]') {
                    $scope.isNotValid = true;
                }
            }
        } else if (step === 2) {
            if ($scope.vpcNetwork !== 'None') {
                if ($scope.securityGroups.length === 0) {
                    $scope.isNotValid = true;
                } 
            }
        } else if (step === 3) {
            if ($scope.availabilityZones.length === 0 && $scope.vpcSubnets.length === 0) {
                $scope.isNotValid = true;
            } else if ($scope.instanceList.length === 0){
                $scope.isNotValid = true;
            }
        } else if (step === 4) {
            // elb name check is needed for the final tab validation
            if ($scope.elbName === '' || $scope.elbName === undefined) {
                $scope.isNotValid = true;
            } else if ($scope.pingPort <= 0 || $scope.pingPort === undefined) {
                $scope.isNotValid = true;
            } else if ($scope.responseTimeout <= 0 || $scope.responseTimeout === undefined) {
                $scope.isNotValid = true;
            } 
        }
        // Signal the parent wizard controller about the update of the validation error status
        $scope.$emit('updateValidationErrorStatus', $scope.isNotValid);
    };
    $scope.getAllSecurityGroups = function (vpc) {
        var csrf_token = $('#csrf_token').val();
        var data = "csrf_token=" + csrf_token + "&vpc_id=" + vpc;
        $http({
            method:'POST', url:$scope.securityGroupJsonEndpoint, data:data,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
        }).success(function(oData) {
            var results = oData ? oData.results : [];
            $scope.securityGroupCollection = results;
        }).error(function (oData) {
            eucaHandleError(oData, status);
        });
    };
    $scope.updateSecurityGroupChoices = function () {
        $scope.securityGroupChoices = {};
        if ($.isEmptyObject($scope.securityGroupCollection)) {
            return;
        }
        $scope.securityGroups = [];
        angular.forEach($scope.securityGroupCollection, function(sGroup){
            var securityGroupName = sGroup.name;
            if (sGroup.name.length > 45) {
                securityGroupName = sGroup.name.substr(0, 45) + "...";
            }
            $scope.securityGroupChoices[sGroup.id] = securityGroupName;
        }); 
        // Timeout is needed for chosen to react after Angular updates the options
        $timeout(function(){
            $('#securitygroup').trigger('chosen:updated');
        }, 500);
    };
    $scope.updateVPCSubnetChoices = function () {
        $scope.vpcSubnetChoices = {};
        $scope.vpcSubnets = [];
        angular.forEach($scope.vpcSubnetList, function(subnet){
            if (subnet.vpc_id === $scope.vpcNetwork) {
                $scope.vpcSubnetChoices[subnet.id] = 
                    subnet.cidr_block + ' (' + subnet.id + ') | ' + 
                    subnet.availability_zone;
            }
        });
        if ($scope.vpcSubnetChoices.length === 0) {
            $scope.vpcSubnetChoices.None = $('#hidden_vpc_subnet_empty_option').text();
            $scope.vpcSubnets.push('None');
        }
        // Timeout is needed for chosen to react after Angular updates the options
        $timeout(function(){
            $('#vpc_subnet').trigger('chosen:updated');
        }, 500);
    };
    $scope.updateVPCNetworkName = function () {
        var vpcNetworkSelectOptions = $('#vpc_network option');
        if (vpcNetworkSelectOptions.length > 0) {
            vpcNetworkSelectOptions.each(function () {
                if ($(this).val() === $scope.vpcNetwork) {
                    $scope.vpcNetworkName = $(this).text();
                }
            });
        }
    };
    $scope.updateSecurityGroupNames = function () {
        $scope.securityGroupNames = [];
        angular.forEach($scope.securityGroups, function (sGroup) {
            $scope.securityGroupNames.push($scope.securityGroupChoices[sGroup]);
        });
    };
    $scope.updateVPCSubnetNames = function () {
        $scope.vpcSubnetNames = [];
        angular.forEach($scope.vpcSubnets, function (vpcSubnet) {
            $scope.vpcSubnetNames.push($scope.vpcSubnetChoices[vpcSubnet]);
        });
    };
    $scope.updateDefaultPingProtocol = function () {
        if ($scope.pingProtocol === 'HTTP' || $scope.pingProtocol === 'TCP') {
           $scope.pingPort = 80;
        } else if ($scope.pingProtocol === 'HTTPS' || $scope.pingProtocol === 'SSL' ) {
           $scope.pingPort = 443;
        }
    };
    $scope.openSelectCertificateModal = function () {
        var modal = $('#select-certificate-modal');
        if (modal.length > 0) {
            modal.foundation('reveal', 'open');
            $scope.certificateRadioButton = 'existing';
            $('#certificate-type-radio-existing').prop('checked', true);
            $('#certificates').val($scope.certificateARN);
            // Remove any empty options created by Angular model issue 
            $('#certificates option').each(function () {
                if ($(this).text() === '') {
                    $(this).remove();
                }
            });
        }
    };
    $scope.selectCertificateTab = function ($event, tab) {
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
        var block = {
            'name': $scope.backendCertificateName,
            'certificateBody': $scope.backendCertificateBody
        };
        return block;
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
        $scope.backendCertificateName = '';
        $scope.backendCertificateBody = '';
    };
    $scope.removeBackendCertificate = function ($event, index) {
        $event.preventDefault();
        $scope.backendCertificateArray.splice(index, 1);
    };
    $scope.setAddBackendCertificateButtonClass = function () {
        if( $scope.isBackendCertificateNotComplete === true || $scope.hasDuplicatedBackendCertificate === true){
            $scope.addBackendCertificateButtonClass = 'disabled';
        } else {
            $scope.addBackendCertificateButtonClass = '';
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
        return block1.name == block2.name;
    };
    $scope.handleCertificateCreate = function ($event, newCertURL) {
        $event.preventDefault();
        if ($scope.certificateRadioButton === 'new') {
            $scope.createNewCertificate(newCertURL);
        }
        var modal = $('#select-certificate-modal');
        if (modal.length > 0) {
            modal.foundation('reveal', 'close');
        }
    };
    $scope.createNewCertificate = function (url) {
        var formData = $('#select-certificate-form').serialize();
        $scope.certificateForm = $('#select-certificate-form');
        $scope.certificateForm.trigger('validate');
        if ($scope.certificateForm.find('[data-invalid]').length) {
            return false;
        }
        var newCertificateName = $scope.newCertificateName;
        $http({
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            method: 'POST',
            url: url,
            data: formData
        }).success(function (oData) {
            Notify.success(oData.message);
            if (oData.id) {
                var newARN = oData.id;
                $('#certificates').append($("<option></option>")
                    .attr("value", newARN)
                    .text(newCertificateName));
                $scope.certificateARN = newARN;
                // timeout is needed for the select element to be updated with the new option
                $timeout(function () {
                    $scope.certificateName = newCertificateName;
                });
            }
        }).error(function (oData) {
            eucaHandleError(oData, status);
        });
    };
    $scope.createELB = function () {
    };
})
;
