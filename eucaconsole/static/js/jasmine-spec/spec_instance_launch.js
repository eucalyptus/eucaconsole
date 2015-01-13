/**
 * @fileOverview Jasmine Unittest for Instance Launch JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("LaunchInstance", function() {

    beforeEach(angular.mock.module('LaunchInstance'));

    var scope, ctrl, httpBackend;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope, $httpBackend) {
        httpBackend = $httpBackend;
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('LaunchInstanceCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of isLoadingKeyPair is false", function() {
            expect(scope.isLoadingKeyPair).not.toBeTruthy();
        });

        it("Initial value of isLoadingSecurityGroup is false", function() {
            expect(scope.isLoadingSecurityGroup).not.toBeTruthy();
        });

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Initial value of instanceVPC is None", function() {
            expect(scope.instanceVPC).toEqual('None');
        });

        it("Initial value of keyPair is empty", function() {
            expect(scope.keyPair).toEqual('');
        });

        it("Initial value of securityGroupVPC is None", function() {
            expect(scope.securityGroupVPC).toEqual('None');
        });

        it("Initial value of subnetVPC is None", function() {
            expect(scope.subnetVPC).toEqual('None');
        });
    });

    describe("Function checkRequiredInput() Test", function() {

        it("Should invalid input when isNotValid is false and imageID is less 12 chars", function() {
            scope.isNotValid = false;
            scope.currentStepIndex = 1;
            scope.imageID = "emi-1234"; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("Should invalid input when imageID is empty, but do not set the imageIDErrorClass", function() {
            scope.isNotValid = true;
            scope.currentStepIndex = 1;
            scope.imageID = ''; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('');
        });

        it("Should invalid input when imageID is more 12 chars", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "emi-1234567890" 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("Should invalid input when imageID is doesn't start with 'emi-'", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "1234567890ab"; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("Should valid input when imageID is 12 chars and begins with 'emi-'", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "emi-12345678"; 
            scope.imageIDErrorClass = 'error';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).not.toBeTruthy();
            expect(scope.imageIDErrorClass).toEqual('');
        });

        it("Should invalid input when instanceNumber is empty", function() {
            scope.currentStepIndex = 2;
            scope.instanceNumber = ''; 
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when keyPair is empty", function() {
            scope.currentStepIndex = 3;
            scope.keyPair = ''; 
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Should invalid input when securityGroups is empty", function() {
            scope.currentStepIndex = 3;
            scope.securityGroups = []; 
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBeTruthy();
        });
    });

    describe("Watch securityGroupVPC Test", function() {

        var vpc = 'vpc-12345678';

        beforeEach(function() {
            setFixtures('<input id="csrf_token" name="csrf_token" type="hidden" value="2a06f17d6872143ed806a695caa5e5701a127ade">');
            scope.jsonEndpoint  = "securitygroup_json";
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + vpc 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
        });

        it("Should broadcast updateVPC when securityGroupVPC is updated", function() {
            spyOn(scope, '$broadcast');
            scope.securityGroupJsonEndpoint = "securitygroup_json";
            scope.instanceVPC = vpc;
            scope.setWatcher();
            scope.securityGroupVPC = vpc;
            scope.$apply();
            expect(scope.$broadcast).toHaveBeenCalledWith('updateVPC', scope.securityGroupVPC);
        });
    });

    describe("Watch instanceVPC Test", function() {

        var vpc = 'vpc-12345678';

        beforeEach(function() {
            setFixtures('<input id="csrf_token" name="csrf_token" type="hidden" value="2a06f17d6872143ed806a695caa5e5701a127ade">');
            scope.jsonEndpoint  = "securitygroup_json";
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + vpc 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
        });

        it("Should call updateSecurityGroupVPC when instanceVPC is updated", function() {
            spyOn(scope, 'updateSecurityGroupVPC');
            scope.securityGroupJsonEndpoint = "securitygroup_json";
            scope.setWatcher();
            scope.instanceVPC = vpc;
            scope.$apply();
            expect(scope.updateSecurityGroupVPC).toHaveBeenCalled();
        });
    });

    describe("Function updateSecurityGroupVPC Test", function() {

        it("Should match securityGroupVPC to instanceVPC when updateSecurityGroupVPC is called", function() {
            scope.instanceVPC = 'vpc-12345678';
            scope.updateSecurityGroupVPC();
            expect(scope.securityGroupVPC).toEqual('vpc-12345678');
        });
    });
});
