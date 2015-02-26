/**
 * @fileOverview Elastic Load Balancer Wizard JS
 * @requires AngularJS
 *
 */

wizardApp.controller('ELBWizardCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
        $scope.elbForm = undefined;
        $scope.urlParams = undefined;
        $scope.isNotValid = true;
        $scope.isListenerNotComplete = false;
        $scope.hasDuplicatedListener = false;
        $scope.elbName = '';
        $scope.listenerArray = []; 
        $scope.protocolList = []; 
        $scope.fromProtocol = '';
        $scope.toProtocol = '';
        $scope.fromPort = '';
        $scope.toPort = '';
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
            $scope.isListenerNotComplete = false;
            $scope.hasDuplicatedListener = false;
            $scope.listenerArray = [];
            $scope.protocolList = options.protocol_list;
            $scope.fromProtocol = $scope.protocolList[0].name;
            $scope.toProtocol = $scope.protocolList[0].name;
            $scope.fromPort = '';
            $scope.toPort = '';
        };
        $scope.setWatcher = function (){
            // Handle the next step tab click event
            $scope.$on('eventClickVisitNextStep', function($event, nextStep) {
                $scope.checkRequiredInput(nextStep);
                // Signal the parent wizard controller about the completion of the next step click event
                $scope.$emit('eventProcessVisitNextStep', nextStep);
            });
            $scope.$watch('elbName', function(){
               $scope.checkRequiredInput(1);
            });
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
        };
        $scope.setFocus = function () {
        };
        $scope.checkRequiredInput = function (step) {
            $scope.isNotValid = false;
            if (step === 1) {
                if ($scope.elbName === '') {
                    $scope.isNotValid = true;
                }
            }
            // Signal the parent wizard controller about the update of the validation error status
            $scope.$emit('updateValidationErrorStatus', $scope.isNotValid);
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
            $scope.checkRequiredInput(1);
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
            $scope.resetValues();
        };
        // Return the matching port given the protocol name
        $scope.getPortFromProtocolList = function (name) {
            var port = '';
            if (name.toLowerCase() === 'tcp') {
                return '';
            }
            angular.forEach($scope.protocolList, function(protocol) {
                if (protocol.name === name) {
                    port = protocol.port;
                }
            }); 
            return port;
        };
        $scope.createELB = function () {
        };
    })
;

