/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
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

        it("should set initial value of isLoadingKeyPair to false", function() {
            expect(scope.isLoadingKeyPair).toBe(false);
        });

        it("should set initial value of isLoadingSecurityGroup to false", function() {
            expect(scope.isLoadingSecurityGroup).toBe(false);
        });

        it("should set initial value of isNotValid to true", function() {
            expect(scope.isNotValid).toBe(true);
        });

        it("should set initial value of instanceVPC is 'None'", function() {
            expect(scope.instanceVPC).toEqual('None');
        });

        it("should set initial value of keyPair to undefined", function() {
            expect(scope.keyPair).toEqual(undefined);
        });

        it("should set initial value of securityGroupVPC to 'None'", function() {
            expect(scope.securityGroupVPC).toEqual('None');
        });

        it("should set initial value of subnetVPC to 'None'", function() {
            expect(scope.subnetVPC).toEqual('None');
        });
    });

    describe("#checkRequiredInput", function() {

        it("should be invalid when isNotValid is false and imageID is less 12 chars", function() {
            scope.isNotValid = false;
            scope.currentStepIndex = 1;
            scope.imageID = "emi-1234"; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("should be invalid when imageID is empty, but do not set the imageIDErrorClass", function() {
            scope.isNotValid = true;
            scope.currentStepIndex = 1;
            scope.imageID = ''; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
            expect(scope.imageIDErrorClass).toEqual('');
        });

        it("should be invalid when imageID is more 12 chars", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "emi-1234567890"; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("should be invalid when imageID is doesn't start with 'emi-'", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "1234567890ab"; 
            scope.imageIDErrorClass = '';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
            expect(scope.imageIDErrorClass).toEqual('error');
        });

        it("should be valid when imageID is 12 chars and begins with 'emi-'", function() {
            scope.currentStepIndex = 1;
            scope.imageID = "emi-12345678"; 
            scope.imageIDErrorClass = 'error';
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(false);
            expect(scope.imageIDErrorClass).toEqual('');
        });

        it("should be invalid when instanceNumber is empty", function() {
            scope.currentStepIndex = 2;
            scope.instanceNumber = ''; 
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });

        it("should be invalid when keyPair is empty", function() {
            scope.currentStepIndex = 3;
            scope.keyPair = ''; 
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });

        it("should be invalid when securityGroups is empty", function() {
            scope.currentStepIndex = 3;
            scope.securityGroups = []; 
            scope.checkRequiredInput(); 
            expect(scope.isNotValid).toBe(true);
        });
    });

    describe("#getAllSecurityGroups", function() {

        var vpc = 'vpc-12345678';

        beforeEach(function() {
            setFixtures('<input id="csrf_token" name="csrf_token" type="hidden" value="2a06f17d6872143ed806a695caa5e5701a127ade">');
            scope.jsonEndpoint  = "securitygroup_json";
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + vpc; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
        });

        afterEach(function() {
            httpBackend.verifyNoOutstandingExpectation();
            httpBackend.verifyNoOutstandingRequest();
        });

        it("should have securityGroupCollection[] initialized after getAllSecurityGroups() is successful", function() {
            scope.securityGroupJsonEndpoint = "securitygroup_json";
            scope.getAllSecurityGroups(vpc);
            httpBackend.flush();
            expect(scope.securityGroupCollection[0]).toEqual('SSH');
            expect(scope.securityGroupCollection[1]).toEqual('HTTP');
            expect(scope.securityGroupCollection[2]).toEqual('HTTPS');
        });
    });

    describe("Watch securityGroupVPC Test", function() {

        var vpc = 'vpc-12345678';

        beforeEach(function() {
            setFixtures('<input id="csrf_token" name="csrf_token" type="hidden" value="2a06f17d6872143ed806a695caa5e5701a127ade">');
            scope.jsonEndpoint  = "securitygroup_json";
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + vpc; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
        });

        it("should broadcast updateVPC when securityGroupVPC is updated", function() {
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
            var data = 'csrf_token=2a06f17d6872143ed806a695caa5e5701a127ade&vpc_id=' + vpc; 
            httpBackend.expect('POST', scope.jsonEndpoint, data)
                .respond(200, {
                    "success": true,
                    "results": ["SSH", "HTTP", "HTTPS"]
                });
        });

        it("should call getInstanceVPCName when instanceVPC is updated", function() {
            spyOn(scope, 'getInstanceVPCName');
            scope.securityGroupJsonEndpoint = "securitygroup_json";
            scope.setWatcher();
            scope.instanceVPC = '';
            scope.$apply();
            scope.instanceVPC = vpc;
            scope.$apply();
            expect(scope.getInstanceVPCName).toHaveBeenCalled();
        });

        it("should call getAllSecurityGroups when instanceVPC is updated", function() {
            spyOn(scope, 'getAllSecurityGroups');
            scope.securityGroupJsonEndpoint = "securitygroup_json";
            scope.setWatcher();
            scope.instanceVPC = '';
            scope.$apply();
            scope.instanceVPC = vpc;
            scope.$apply();
            expect(scope.getAllSecurityGroups).toHaveBeenCalled();
        });

        it("should call updateVPCSubnetChoices when instanceVPC is updated", function() {
            spyOn(scope, 'updateVPCSubnetChoices');
            scope.securityGroupJsonEndpoint = "securitygroup_json";
            scope.setWatcher();
            scope.instanceVPC = vpc;
            scope.$apply();
            expect(scope.updateVPCSubnetChoices).toHaveBeenCalled();
        });

        it("should call updateSecurityGroupVPC when instanceVPC is updated", function() {
            spyOn(scope, 'updateSecurityGroupVPC');
            scope.securityGroupJsonEndpoint = "securitygroup_json";
            scope.setWatcher();
            scope.instanceVPC = '';
            scope.$apply();
            scope.instanceVPC = vpc;
            scope.$apply();
            expect(scope.updateSecurityGroupVPC).toHaveBeenCalled();
        });
    });

    describe("#updateSecurityGroupVPC", function() {

        it("should match securityGroupVPC to instanceVPC when updateSecurityGroupVPC is called", function() {
            scope.instanceVPC = 'vpc-12345678';
            scope.updateSecurityGroupVPC();
            expect(scope.securityGroupVPC).toEqual('vpc-12345678');
        });
    });

    describe("#getInstanceVPCName", function() {

        beforeEach(function() {
            setFixtures('<select id="vpc_network"><option value="vpc-12345678">VPC-01</option><option value="vpc-12345679">VPC-02</option></select>');
        });

        it("should update instanceVPCName when getInstanceVPCName is called", function() {
            scope.getInstanceVPCName('vpc-12345678');
            expect(scope.instanceVPCName).toEqual('VPC-01');
        });
    });

    describe("#updateSelectedSecurityGroupRules", function() {

        it("should set securityGroups to [] if it is undefined when updateSelectedSecurityGroupRules is called", function() {
            scope.securityGroups = undefined;
            scope.updateSelectedSecurityGroupRules();
            expect(scope.securityGroups).toEqual([]);
        });
    });
});
