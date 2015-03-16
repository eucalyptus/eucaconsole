/**
 * @fileOverview Elastic Load Balander Listener Editor Directive JS
 * @requires AngularJS
 *
 */
angular.module('EucaConsoleUtils').directive('elbListenerEditor', function() {
        return {
            restrict: 'E',
            scope: {
                option_json: '@options'
            },
            templateUrl: function (scope, elem) {
                return elem.template;
            },
            controller: function ($scope, $timeout, eucaHandleError, eucaUnescapeJson) {
		$scope.isListenerNotComplete = true;
		$scope.hasDuplicatedListener = false;
                $scope.listenerArray = []; 
                $scope.protocolList = []; 
                $scope.toProtocolList = []; 
                $scope.fromProtocol = '';
                $scope.toProtocol = '';
                $scope.fromPort = '';
                $scope.toPort = '';
                $scope.portRangePattern = '';
                $scope.isFromProtocolValid = false;
                $scope.serverCertificateName = '';
                $scope.elbListenerTextarea = undefined;
                $scope.addListenerButtonClass = 'disabled';
		$scope.initEditor = function () {
		    var options = JSON.parse(eucaUnescapeJson($scope.option_json));
		    $scope.setInitialValues(options);
		    $scope.setWatcher();
		    $scope.setFocus();
		};
		$scope.setInitialValues = function (options) {
                    if ($('#elb-listener').length > 0) {
                        $scope.elbListenerTextarea = $('#elb-listener');
                    }
                    $scope.protocolList = []; 
                    $scope.toProtocolList = []; 
                    $scope.protocolList.push({'name': 'Select...', 'value': 'None', 'port': ''});
                    $scope.fromProtocol = $scope.protocolList[0].value;
		    $scope.toProtocol = $scope.protocolList[0].value;
                    $scope.fromPort = $scope.protocolList[0].port;
		    $scope.toPort = $scope.protocolList[0].port;
                    if (options.hasOwnProperty('protocol_list')) {
                        if (options.protocol_list instanceof Array && options.protocol_list.length > 0) {
		            $scope.protocolList = $scope.protocolList.concat(options.protocol_list);
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
			$scope.fromPort = $scope.getPortFromProtocolList($scope.fromProtocol);
                        $scope.checkAddListenerButtonCondition(); 
                        $scope.adjustToProtocolList();
		    });
		    $scope.$watch('toProtocol', function(){
			$scope.toPort = $scope.getPortFromProtocolList($scope.toProtocol);
                        $scope.checkAddListenerButtonCondition(); 
		    });
		    $scope.$watch('fromPort', function(){
                        $scope.checkAddListenerButtonCondition(); 
                        $scope.validateFromProtocol(); 
		    });
		    $scope.$watch('toPort', function(){
                        $scope.checkAddListenerButtonCondition(); 
		    });
		    $scope.$watch('isListenerNotComplete', function () {
			$scope.setAddListenerButtonClass(); 
		    });
		    $scope.$watch('hasDuplicatedListener', function () {
			$scope.setAddListenerButtonClass(); 
		    });
                    $scope.$watch('listenerArray', function () {
                        $scope.$emit('eventUpdateListenerArray', $scope.listenerArray);
                    }, true);
		    $scope.$on('eventUpdateCertificateName', function ($event, name) {
                        $scope.serverCertificateName = name;
		    });
		};
		$scope.setFocus = function () {
                };
		// In case of the duplicated listener, add the 'disabled' class to the button
		$scope.setAddListenerButtonClass = function () {
		    if( $scope.isListenerNotComplete === true || $scope.hasDuplicatedListener === true){
			$scope.addListenerButtonClass = 'disabled';
		    } else {
			$scope.addListenerButtonClass = '';
		    }
		};
		$scope.resetValues = function () {
		    $scope.fromProtocol = $scope.protocolList[0].value;
		    $scope.toProtocol = $scope.protocolList[0].value;
                    $scope.isFromProtocolValid = false;
		};
		$scope.checkForDuplicatedListeners = function () {
		    $scope.hasDuplicatedListener = false;
		    // Create a new array block based on the current user input on the panel
		    var newBlock = $scope.createListenerArrayBlock();
		    for( var i=0; i < $scope.listenerArray.length; i++){
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
			block1.fromProtocol == block2.fromProtocol &&
			block1.toProtocol == block2.toProtocol) {
			return true;
		    }
		    return false;
		};
		$scope.createListenerArrayBlock = function () {
		    var block = {
			'fromProtocol': $scope.fromProtocol,
			'fromPort': $scope.fromPort,
			'toProtocol': $scope.toProtocol,
			'toPort': $scope.toPort,
		    };
		    return block;
		};
		$scope.addListener = function ($event) {
		    $event.preventDefault();
                    $scope.checkAddListenerButtonCondition(); 
		    if ($scope.isListenerNotComplete === true || $scope.hasDuplicatedListener === true) {
			return false;
		    }
		    // Add the listener 
		    $scope.listenerArray.push($scope.createListenerArrayBlock());
                    $scope.syncListeners();
		    $scope.$emit('listenerArrayUpdate');
		};
		$scope.removeListener = function ($event, index) {
		    $event.preventDefault();
		    $scope.listenerArray.splice(index, 1);
		    $scope.syncListeners();
		    $scope.$emit('listenerArrayUpdate');
		};
		$scope.syncListeners = function () {
                    $scope.elbListenerTextarea.val(JSON.stringify($scope.listenerArray));
		    $scope.resetValues();
                    $scope.checkAddListenerButtonCondition(); 
		};
                $scope.checkAddListenerButtonCondition = function () {
                    $scope.isListenerNotComplete = true;
                    if ($scope.fromProtocol === 'None' || $scope.toProtocol === 'None') {
                        return false;
                    } else if ($scope.fromPort === '' || $scope.toPort === '') {
                        return false;
                    } else { 
                        $scope.isListenerNotComplete = false;
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
                    if ($scope.fromPort !== '') {
                        $scope.isFromProtocolValid = true;
                    }
                }; 
                $scope.adjustToProtocolList = function () {
                    $scope.toProtocolList = [];
                    $scope.toProtocolList.push({'name': 'Select...', 'value': 'None', 'port': ''});
		    $scope.toProtocol = $scope.protocolList[0].value;
		    $scope.toPort = $scope.protocolList[0].port;
                    if ($scope.fromProtocol === 'HTTP' || $scope.fromProtocol === 'HTTPS') {
                        angular.forEach($scope.protocolList, function (protocol) {
                            if (protocol.value === 'HTTP' || protocol.value === 'HTTPS') {
                                $scope.toProtocolList.push(protocol);
                            }
                        });
                    } else if ($scope.fromProtocol === 'TCP' || $scope.fromProtocol === 'SSL') {
                        angular.forEach($scope.protocolList, function (protocol) {
                            if (protocol.value === 'TCP' || protocol.value === 'SSL') {
                                $scope.toProtocolList.push(protocol);
                            }
                        });
                    }
                };
                $scope.openCertificateModal = function () {
                    $scope.$emit('eventOpenSelectCertificateModal');
                };
                $scope.initEditor();
            }
        };
    })
;
