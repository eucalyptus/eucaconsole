/**
 * @fileOverview Elastic Load Balander Listener Editor Directive JS
 * @requires AngularJS
 *
 */

eucaConsoleUtils.directive('elbListenerEditor', function() {
        return {
            restrict: 'E',
            scope: {
                option_json: '@options'
            },
            templateUrl: function (scope, elem) {
                return elem.template;
            },
            controller: function ($scope, $timeout, eucaHandleError, eucaUnescapeJson) {
		$scope.isListenerNotComplete = false;
		$scope.hasDuplicatedListener = false;
                $scope.listenerArray = []; 
                $scope.protocolList = []; 
                $scope.fromProtocol = '';
                $scope.toProtocol = '';
                $scope.fromPort = '';
                $scope.toPort = '';
                $scope.portRangePattern = '';
                $scope.serverCertificateName = '';
                $scope.elbListenerTextarea = undefined;
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
                    if (options.hasOwnProperty('protocol_list')) {
		        $scope.protocolList = options.protocol_list;
                        if ($scope.protocolList instanceof Array && $scope.protocolList.length > 0) {
		            $scope.fromProtocol = $scope.protocolList[0].name;
		            $scope.toProtocol = $scope.protocolList[0].name;
                        }
                    }
                    if (options.hasOwnProperty('port_range_pattern')) {
                        $scope.portRangePattern = options.port_range_pattern;
                    }
                    // If serverCertificateName is empty, set it to the selected option name of the #certificates select list
                    if ($scope.serverCertificateName === '' && $('#certificates option:selected').length > 0) {
                        $scope.serverCertificateName = $('#certificates option:selected').text();
                    }
		};
		$scope.setWatcher = function () {
		    $scope.$watch('fromProtocol', function(){
			$scope.fromPort = $scope.getPortFromProtocolList($scope.fromProtocol);
			$scope.checkForDuplicatedListeners();
		    });
		    $scope.$watch('toProtocol', function(){
			$scope.toPort = $scope.getPortFromProtocolList($scope.toProtocol);
			$scope.checkForDuplicatedListeners();
		    });
		    $scope.$watch('fromPort', function(){
			$scope.checkForDuplicatedListeners();
		    });
		    $scope.$watch('toPort', function(){
			$scope.checkForDuplicatedListeners();
		    });
		    $scope.$watch('isListenerNotComplete', function () {
			$scope.setAddListenerButtonClass(); 
		    });
		    $scope.$watch('hasDuplicatedListener', function () {
			$scope.setAddListenerButtonClass(); 
		    });
		    $scope.$on('eventUpdateCertificateName', function ($event, name) {
                        console.log("on " + name);
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
		    $scope.fromProtocol = $scope.protocolList[0].name;
		    $scope.toProtocol = $scope.protocolList[0].name;
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
		    $scope.checkForDuplicatedListeners(); 
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
                $scope.openCertificateModal = function () {
                    $scope.$emit('eventOpenSelectCertificateModal');
                };
                $scope.initEditor();
            }
        };
    })
;
