/**
 * @fileOverview Elastic Load Balancer Wizard JS
 * @requires AngularJS
 *
 */

wizardApp.controller('ELBWizardCtrl', function ($scope, $http, $timeout, eucaHandleError, eucaUnescapeJson) {
        $scope.elbForm = undefined;
        $scope.urlParams = undefined;
        $scope.isNotValid = true;
        $scope.securityGroupJsonEndpoint = '';
        $scope.elbName = '';
        $scope.vpcNetwork = '';
        $scope.vpcSubnet = '';
        $scope.vpcSubnetChoices = [];
        $scope.securityGroups = [];
        $scope.securityGroupChoices = [];
        $scope.securityGroupCollection = []; 
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
            $scope.initChosenSelectors(); 
        };
        $scope.initChosenSelectors = function () {
            $('#securitygroup').chosen({'width': '100%', search_contains: true});
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
            $scope.$watch('vpcNetwork', function () {
                $scope.getAllSecurityGroups($scope.vpcNetwork);
            });
            $scope.$watch('securityGroupCollection', function () {
                $scope.updateSecurityGroupChoices();
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
        $scope.createELB = function () {
        };
    })
;

