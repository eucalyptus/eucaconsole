/**
 * @fileOverview Elastic Load Balander Listener Editor JS
 * @requires AngularJS
 *
 */
angular.module('ELBListenerEditor', ['EucaConsoleUtils'])
    .controller('ELBListenerEditorCtrl', function ($scope, $timeout, eucaHandleError, eucaUnescapeJson) {
        $scope.isListenerNotComplete = true;
        $scope.hasDuplicatedListener = false;
        $scope.hasDuplicatedFromPorts = false;
        $scope.listenerArray = []; 
        $scope.protocolList = []; 
        $scope.toProtocolList = []; 
        $scope.fromProtocol = undefined;
        $scope.toProtocol = undefined;
        $scope.fromPort = '';
        $scope.toPort = '';
        $scope.portRangePattern = '';
        $scope.isFromProtocolValid = false;
        $scope.classFromPortDiv = '';
        $scope.classToPortDiv = '';
        $scope.classDuplicatedFromPortDiv = '';
        $scope.classDuplicatedListenerDiv = '';
        $scope.classNoListenerWarningDiv = '';
        $scope.elbListenerTextarea = undefined;
        $scope.serverCertificateName = '';
        $scope.serverCertificateARN = '';
        $scope.serverCertificateARNBlock = {};
        $scope.addListenerButtonClass = 'disabled';
        $scope.initEditor = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.setInitialValues(options);
            $scope.setWatcher();
            // Workaround for the Bug in jQuery to prevent JS Uncaught TypeError
            // See http://stackoverflow.com/questions/27408501/ng-repeat-sorting-is-throwing-an-exception-in-jquery
            Object.getPrototypeOf(document.createComment('')).getAttribute = function() {};
        };
        $scope.setInitialValues = function (options) {
            if ($('#elb-listener').length > 0) {
                $scope.elbListenerTextarea = $('#elb-listener');
            }
            $scope.protocolList = []; 
            $scope.toProtocolList = []; 
            $scope.protocolList.push({'name': 'Select...', 'value': 'None', 'port': ''});
            $scope.fromProtocol = $scope.protocolList[0];
            $scope.toProtocol = $scope.protocolList[0];
            $scope.fromPort = $scope.protocolList[0].port;
            $scope.toPort = $scope.protocolList[0].port;
            if (options.hasOwnProperty('protocol_list')) {
                if (options.protocol_list instanceof Array && options.protocol_list.length > 0) {
                    $scope.protocolList = $scope.protocolList.concat(options.protocol_list);
                }
            }
            if (options.hasOwnProperty('listener_list')) {
                if (options.listener_list instanceof Array && options.listener_list.length > 0) {
                    $scope.setInitialListenerArray(options.listener_list);
                    if ($scope.listenerArray.length > 0) {
                        $scope.elbListenerTextarea.val(JSON.stringify($scope.listenerArray));
                    }
                }
            }
            if (options.hasOwnProperty('port_range_pattern')) {
                $scope.portRangePattern = options.port_range_pattern;
            }
            $scope.isFromProtocolValid = false;
            // If serverCertificateName is empty, set it to the selected option name of the #certificates select list
            if ($scope.serverCertificateName === '' && $('#certificates option:selected').length > 0) {
                $scope.serverCertificateName = $('#certificates option:selected').text();
            }
        };
        $scope.setWatcher = function () {
            $scope.$watch('fromProtocol', function(){
                $scope.fromPort = parseInt($scope.fromProtocol.port);
                $scope.checkAddListenerButtonCondition();
                $scope.adjustToProtocolList();
            });
            $scope.$watch('toProtocol', function(){
                $scope.toPort = parseInt($scope.toProtocol.port);
                $scope.checkAddListenerButtonCondition();
            });
            $scope.$watch('fromPort', function(){
                $scope.checkForDuplicatedFromPorts();
                $scope.checkAddListenerButtonCondition(); 
                $scope.validateFromProtocol();
            });
            $scope.$watch('toPort', function(){
                $scope.checkAddListenerButtonCondition();
            });
            $scope.$watch('classToPortDiv', function () {
                if ($scope.classToPortDiv === 'error'){
                    $scope.isListenerNotComplete = true;
                }
            });
            $scope.$watch('classFromPortDiv', function () {
                if ($scope.classFromPortDiv === 'error'){
                    $scope.isListenerNotComplete = true;
                }
            });
            $scope.$watch('isListenerNotComplete', function () {
                $scope.setAddListenerButtonClass();
            });
            $scope.$watch('hasDuplicatedFromPort', function () {
                $scope.setAddListenerButtonClass(); 
                $scope.classDuplicatedFromPortDiv = '';
                // timeout is needed for the DOM update to complete
                $timeout(function () {
                    if ($scope.hasDuplicatedFromPort === true) {
                        $scope.classDuplicatedFromPortDiv = 'error';
                    }
                });
            });
            $scope.$watch('hasDuplicatedListener', function () {
                $scope.setAddListenerButtonClass(); 
                $scope.classDuplicatedListenerDiv = '';
                // timeout is needed for the DOM update to complete
                $timeout(function () {
                    if ($scope.hasDuplicatedListener === true) {
                        $scope.classDuplicatedListenerDiv = 'error';
                    }
                });
            });
            $scope.$watch('listenerArray', function () {
                if ($scope.listenerArray.length > 0) {
                    $scope.classNoListenerWarningDiv = '';
                }
                $scope.$emit('eventUpdateListenerArray', $scope.listenerArray);
            }, true);
            $scope.$on('eventUpdateCertificateName', function ($event, name) {
                $scope.serverCertificateName = name;
            });
            $scope.$on('eventUpdateCertificateARN', function ($event, arn, block) {
                $scope.serverCertificateARN = arn;
                $scope.serverCertificateARNBlock = block;
            });
            $scope.$on('eventUseThisCertificate', function ($event, arn, name) {
                $scope.serverCertificateARN = arn;
                $scope.serverCertificateName = name;
                $scope.handleEventUseThisCertificate();
            });
        };
        // In case of the duplicated listener, add the 'disabled' class to the button
        $scope.setAddListenerButtonClass = function () {
            if ($scope.isListenerNotComplete === true ||
                $scope.hasDuplicatedFromPort === true ||
                $scope.hasDuplicatedListener === true) {
                $scope.addListenerButtonClass = 'disabled';
            } else {
                $scope.addListenerButtonClass = '';
            }
        };
        $scope.resetValues = function () {
            $scope.fromProtocol = $scope.protocolList[0];
            $scope.toProtocol = $scope.protocolList[0];
            $scope.isFromProtocolValid = false;
        };
        $scope.checkForDuplicatedFromPorts = function () {
            $scope.hasDuplicatedFromPort = false;
            angular.forEach($scope.listenerArray, function (block) {
                if (block.fromPort === $scope.fromPort) {
                    $scope.hasDuplicatedFromPort = true;
                }
            });
            return;
        };
        $scope.checkForDuplicatedListeners = function () {
            $scope.hasDuplicatedListener = false;
            // Create a new array block based on the current user input on the panel
            var newBlock = $scope.createListenerArrayBlock();
            for(var i=0; i < $scope.listenerArray.length; i++){
                // Compare the new array block with the existing ones
                if( $scope.compareListeners(newBlock, $scope.listenerArray[i]) ){
                    $scope.hasDuplicatedListener = true;
                    return;
                }
            }
            return;
        };
        $scope.compareListeners = function (block1, block2) {
            if (block1.fromPort == block2.fromPort &&
                block1.toPort == block2.toPort &&
                block1.fromProtocol.value == block2.fromProtocol.value &&
                block1.toProtocol.value == block2.toProtocol.value) {
                return true;
            }
            return false;
        };
        $scope.createListenerArrayBlock = function () {
            var block = {
                'fromProtocol': $scope.fromProtocol.value,
                'fromPort': $scope.fromPort,
                'toProtocol': $scope.toProtocol.value,
                'toPort': $scope.toPort,
            };
            if (block.fromProtocol === 'HTTPS' || block.fromProtocol === 'SSL') {
                block.certificateARN = $scope.serverCertificateARN;
                block.certificateName = $scope.serverCertificateName;
            }
            return block;
        };
        $scope.setInitialListenerArray = function (listener_list) {
            angular.forEach(listener_list, function (listener) {
                var block = {
                    'fromProtocol': listener.protocol,
                    'fromPort': listener.from_port,
                    'toProtocol': listener.protocol,
                    'toPort': listener.to_port,
                };
                $scope.listenerArray.push(block);
            });
        };
        $scope.addListener = function ($event) {
            $event.preventDefault();
            $scope.checkAddListenerButtonCondition(); 
            // timeout is needed for all DOM updates and validations to be complete
            $timeout(function () {
                if ($scope.isListenerNotComplete === true ||
                    $scope.hasDuplicatedFromPort === true ||
                    $scope.hasDuplicatedListener === true) {
                    return false;
                }
                // Add the listener 
                $scope.listenerArray.push($scope.createListenerArrayBlock());
                $scope.syncListeners();
                $scope.$emit('eventUpdateListenerArray', $scope.listenerArray);
            });
        };
        $scope.removeListener = function (index) {
            $scope.listenerArray.splice(index, 1);
            $scope.syncListeners();
            $scope.$emit('eventUpdateListenerArray', $scope.listenerArray);
            if ($scope.listenerArray.length === 0) {
                $scope.classNoListenerWarningDiv = 'error';
            }
        };
        $scope.cancelListener = function ($event) {
            $event.preventDefault();
            $scope.resetValues();
            $scope.classDuplicatedFromPortDiv = '';
            $scope.classDuplicatedListenerDiv = '';
            $scope.classNoListenerWarningDiv = '';
            $scope.addListenerButtonClass = 'disabled';
            $timeout(function () {
                $scope.$emit('requestValidationCheck');
            });
        };
        $scope.syncListeners = function () {
            $scope.elbListenerTextarea.val(JSON.stringify($scope.listenerArray));
            $scope.resetValues();
            $scope.checkAddListenerButtonCondition(); 
            // timeout is needed for all DOM updates and validations to complete
            $timeout(function () {
                $scope.$emit('requestValidationCheck');
            });
        };
        $scope.checkAddListenerButtonCondition = function () {
            if ($scope.fromProtocol.value === undefined || $scope.toProtocol.value === undefined) {
                $scope.isListenerNotComplete = true;
            } else if ($scope.fromProtocol.value === 'None' || $scope.toProtocol.value === 'None') {
                $scope.isListenerNotComplete = true;
            } else if ($scope.fromPort === '' || $scope.toPort === '') {
                $scope.isListenerNotComplete = true;
            } else {
                $scope.isListenerNotComplete = false;
            }
            if ($scope.isListenerNotComplete === false) {
                $scope.checkFromPortInputCondition();
                $scope.checkToPortInputCondition();
                $scope.checkForDuplicatedListeners();
            }
        };
        // Return the matching port given the protocol name
        $scope.getPortFromProtocolList = function (name) {
            var port = '';
            angular.forEach($scope.protocolList, function(protocol) {
                if (protocol.name === name) {
                    port = protocol.port;
                }
            });
            return port;
        };
        $scope.validateFromProtocol = function () {
            if ($scope.fromProtocol.value !== undefined &&
                $scope.fromProtocol.value !== 'None' &&
                !isNaN($scope.fromPort)) {
                $scope.isFromProtocolValid = true;
            }
        }; 
        $scope.adjustToProtocolList = function () {
            var newProtocolList = [];
            newProtocolList.push({'name': 'Select...', 'value': 'None', 'port': ''});
            $scope.toProtocol = $scope.protocolList[0];
            $scope.toPort = $scope.protocolList[0].port;
            if ($scope.fromProtocol.value === 'HTTP' || $scope.fromProtocol.value === 'HTTPS') {
                angular.forEach($scope.protocolList, function (protocol) {
                    if (protocol.value === 'HTTP' || protocol.value === 'HTTPS') {
                        newProtocolList.push(protocol);
                    }
                });
            } else if ($scope.fromProtocol.value === 'TCP' || $scope.fromProtocol.value === 'SSL') {
                angular.forEach($scope.protocolList, function (protocol) {
                    if (protocol.value === 'TCP' || protocol.value === 'SSL') {
                        newProtocolList.push(protocol);
                    }
                });
            }
            $scope.toProtocolList = newProtocolList;
        };
        $scope.checkFromPortInputCondition = function () {
            $scope.classFromPortDiv = "";
            // timeout is needed for the update of the input element DOM to be completed
            $timeout(function () {
                if ($('#from-port-input').hasClass('ng-invalid-pattern')) {
                    $scope.classFromPortDiv = "error";
                }
            });
        }; 
        $scope.checkToPortInputCondition = function () {
            $scope.classToPortDiv = "";
            // timeout is needed for the update of the input element DOM to be completed
            $timeout(function () {
                if ($('#to-port-input').hasClass('ng-invalid-pattern')) {
                    $scope.classToPortDiv = "error";
                }
            });
        }; 
        $scope.showSelectCertificateModalLink = function () {
            if ($scope.toPort === '' || $scope.fromPort === '') {
                return false;
            }
            if ($scope.fromProtocol.value === 'HTTPS' ||
                $scope.fromProtocol.value === 'SSL' ||
                $scope.toProtocol.value === 'HTTPS' ||
                $scope.toProtocol.value === 'SSL') {
                return true;
            }
            return false;
        };
        $scope.showServerCertificateNameLink = function (fromProtocol) {
            if (fromProtocol === 'HTTPS' || fromProtocol === 'SSL') { 
                return true;
            }
            return false;
        };
        $scope.showBackendCertificateLink = function (fromProtocol, toProtocol) {
            if (fromProtocol === 'HTTPS' || fromProtocol === 'SSL') {
                return false;
            } else if (toProtocol === 'HTTPS' || toProtocol === 'SSL') {
                return true;
            }
            return false;
        };
        $scope.openCertificateModal = function (fromProtocol, toProtocol, fromPort, toPort) {
            var certificateTab = 'SSL';
            if (fromProtocol !== 'HTTPS' && fromProtocol !== 'SSL') {
                certificateTab = 'BACKEND';
            }
            $scope.$emit('eventOpenSelectCertificateModal', fromProtocol, toProtocol, fromPort, toPort, certificateTab);
        };
        $scope.handleEventUseThisCertificate = function () {
            angular.forEach($scope.listenerArray, function (block) {
                if (block.fromPort === $scope.serverCertificateARNBlock.fromPort &&
                    block.toPort === $scope.serverCertificateARNBlock.toPort) {
                    block.certificateARN = $scope.serverCertificateARN;
                    block.certificateName = $scope.serverCertificateName;
                    $scope.elbListenerTextarea.val(JSON.stringify($scope.listenerArray));
                    $scope.$emit('eventUpdateListenerArray', $scope.listenerArray);
                }
            });
        };
    })
;
