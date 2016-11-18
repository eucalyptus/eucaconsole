/**
 * @fileOverview Jasmine Unit test for ELBWizard module.
 */

describe('ELB Wizard Module', function () {
    
    beforeEach(angular.mock.module('ELBWizard'));

    var $compile, $rootScope, $location, $browser, $timeout;

    beforeEach(angular.mock.inject(
        function (_$compile_, _$rootScope_, _$templateCache_, _$location_, _$timeout_) {
            $compile = _$compile_;
            $rootScope = _$rootScope_;
            $templateCache = _$templateCache_;
            $location = _$location_;
            $timeout = _$timeout_;
        }
    ));

    describe('ELBWizardService', function () {

        var ELBWizardService, steps;

        beforeEach(angular.mock.inject(function (_ELBWizardService_) {
            ELBWizardService = _ELBWizardService_;
            steps = [
                {
                    label: 'General',
                    href: '/elbs/wizard/',
                    vpcOnly: false,
                    complete: false
                },
                {
                    label: 'Network',
                    href: '/elbs/wizard/network',
                    vpcOnly: true,
                    complete: false
                },
                {
                    label: 'Instances',
                    href: '/elbs/wizard/instances',
                    vpcOnly: false,
                    complete: false
                },
                {
                    label: 'Health Check & Advanced',
                    href: '/elbs/wizard/advanced',
                    vpcOnly: false,
                    complete: false
                }
            ];
        }));

        describe('the service', function () {

            it('should default certsAvailable', function () {
                expect(ELBWizardService.certsAvailable).toEqual([]);
            });

            it('should default policies', function () {
                expect(ELBWizardService.policies).toEqual([]);
            });
        });

        describe('#initNav', function () {

            it('should return a navigation object with the correct number of steps', function () {
                var nav = ELBWizardService.initNav(steps);
                expect(nav.steps.length).toEqual(steps.length);
            });
        });

        describe('#next', function () {

            var nav, current;

            beforeEach(function () {
                nav = ELBWizardService.initNav(steps);
                spyOn(nav, 'next').and.callThrough();

                current = nav.current;  // Save a reference to the original "current" for testing later
                ELBWizardService.next({
                    name: 'foo'
                });
            });

            it('should update wizard state with current step values', function () {
                expect(ELBWizardService.values).toEqual(jasmine.objectContaining({
                    name: 'foo'
                }));
            });

            it('should set current step to complete', function () {
                expect(current.complete).toBe(true);
            });

            it('should advance to the next step', function () {
                expect(nav.next).toHaveBeenCalled();
            });
        });

        describe('#submit', function () {

            it('should call a backend service to create the ELB', function () {
            });
        });
    });

    describe('wizardNav directive', function () {

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/wizard/navigation.pt'];
            $templateCache.put('/_template/elbs/wizard/navigation', template);
        }));

        var element, scope, controller;
        beforeEach(function () {
            element = $compile(
                '<div elb-wizard="" cloud-type="euca"><wizard-nav></wizard-nav></div>'
            )($rootScope);
            $rootScope.$digest();

            scope = element.isolateScope();

            $location.path('/elbs/wizard/');
            $rootScope.$apply();

            var nav = element.find('wizard-nav');
            controller = nav.controller('wizardNav');
        });

        it('should default to the first tab', function () {
            var tab = angular.element(element.find('dd')[0]);
            expect(tab.hasClass('active')).toBe(true);
        });

        it('should activate the appropriate tab to active based upon path', function () {
            $location.path('/elbs/wizard/instances');
            $rootScope.$apply();

            var current = controller.status({
                href: '/elbs/wizard/instances'
            });

            expect(current).toEqual(jasmine.objectContaining({
                active: true
            }));
        });

        it('should not allow navigation to disabled tabs', function () {
            var href = controller.visit({
                complete: false,
                href: '/foo/bar/baz'
            });
            expect(href).toEqual('');
        });

        it('should allow navigation to enabled tabs', function () {
            var href = controller.visit({
                complete: true,
                href: '/foo/bar/baz'
            });
            expect(href).toEqual('/foo/bar/baz');
        });
    });

    describe('focusOnLoad directive', function () {

        var element;
        beforeEach(function () {
            element = $compile(
                '<input type="text" focus-on-load="1"/>'
            )($rootScope);
            $rootScope.$digest();

            spyOn(element[0], 'focus');

            $timeout.flush();
        });

        it('should have focus on compile', function () {
            expect(element[0].focus).toHaveBeenCalled();
        });
    });

    describe('Main page controller', function () {
    });

    describe('General tab controller', function () {

        var element, scope, ModalService, ELBWizardService;

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/wizard/general.pt'];
            $templateCache.put('/_template/elbs/wizard/general', template);
        }));

        beforeEach(angular.mock.inject(function ($injector) {
            $httpBackend = $injector.get('$httpBackend');
            $httpBackend.when('GET', '/certificate').respond(
                    200, '[]');
        }));

        var $controller, $routeParams, $location, controller;
        beforeEach(inject(function (_$controller_, _$routeParams_, _$location_, _ModalService_, _ELBWizardService_) {
            scope = $rootScope.$new();
            scope.stepData = {
                certificates: []
            };

            $controller = _$controller_;
            $routeParams = _$routeParams_;
            $location = _$location_;

            ModalService = _ModalService_;
            ELBWizardService = _ELBWizardService_;

            spyOn(ELBWizardService, 'next');

            controller = $controller('GeneralController', {
                $scope: scope,
                $routeParams: $routeParams,
                $location: $location,
                ModalService: ModalService,
                ELBWizardService: ELBWizardService,
                certificates: [],
                policies: []
            });
        }));

        it('should add one default listener', function () {
            expect(controller.values.listeners.length).toEqual(1);
        });

        describe('#submit', function () {

            beforeEach(function () {
                scope.generalForm = {};
            });

            it('should move to next step on submit when valid', function () {
                scope.generalForm.$invalid = false;

                controller.submit();
                expect(ELBWizardService.next).toHaveBeenCalled();
            });

            it('should not move to next step on submit when invalid', function () {
                scope.generalForm.$invalid = true;

                controller.submit();
                expect(ELBWizardService.next).not.toHaveBeenCalled();
            });
        });
    });

    describe('Network tab controller', function () {

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/wizard/network.pt'];
            $templateCache.put('/_template/elbs/wizard/network', template);
        }));

        var $controller, $routeParams, controller;
        beforeEach(inject(function (_$controller_, _$routeParams_) {
            var $scope = $rootScope.$new();

            $controller = _$controller_;
            $routeParams = _$routeParams_;

            controller = $controller('NetworkController', {
                $scope: $scope,
                $routeParams: $routeParams
            });
        }));

        it('should set initial value of vpcNetwork to "None"', function () {
            expect(controller.vpcNetwork).toEqual('None');
        });

        it('should set initial value of vpcSecurityGroupChoices to an empty array', function () {
            expect(controller.vpcSecurityGroupChoices).toEqual([]);
        });

    });

    describe('Instances tab controller', function () {

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/wizard/instances.pt'];
            $templateCache.put('/_template/elbs/wizard/instances', template);
        }));

        var $controller, $scope, $routeParams, controller;
        beforeEach(inject(function (_$controller_, _$routeParams_) {
            $scope = $rootScope.$new();

            $controller = _$controller_;
            $routeParams = _$routeParams_;

            controller = $controller('InstancesController', {
                $scope: $scope,
                $routeParams: $routeParams
            });
        }));

        beforeEach(function() {
            controller.instances = [
                {availability_zone: 'one', subnet_id: 'subnet-10000001', selected: false},
                {availability_zone: 'one', subnet_id: 'subnet-10000001', selected: false},
                {availability_zone: 'two', subnet_id: 'subnet-10000002', selected: false}
            ];
            controller.vpcNetwork = 'vpc-abcdefg';
        });

        it('should deselect instance when zone deselected', function() {
            // select 1 from each zone
            controller.instances[0].selected = true;
            controller.instances[2].selected = true;
            // set 2 zones in model
            var zones = [
                {id:'one', label:'one'},
                {id:'two', label:'two'}
            ];
            controller.handleDeselection([zones[0]], zones, 'availability_zone');
            expect(controller.instances[0].selected).toBe(true);
            expect(controller.instances[1].selected).toBe(false);
            expect(controller.instances[2].selected).toBe(false);
        });

        it('should deselect instance when subnet deselected', function() {
            // select 1 from each zone
            controller.instances[0].selected = true;
            controller.instances[2].selected = true;
            // set 2 subnets in model
            var subnets = [
                {id:'subnet-10000001', label:'subnet1'},
                {id:'subnet-10000002', label:'subnet2'}
            ];
            controller.handleDeselection([subnets[0]], subnets, 'subnet_id');
            expect(controller.instances[0].selected).toBe(true);
            expect(controller.instances[1].selected).toBe(false);
            expect(controller.instances[2].selected).toBe(false);
        });

        it('should select zone when instance selected', function() {
            controller.vpcNetwork = 'None';
            // set 2 zones in model
            controller.availabilityZoneChoices = [
                {id:'one', label:'one'},
                {id:'two', label:'two'}
            ];
            controller.availabilityZones = [];
            // select 1 instance
            controller.instances[0].selected = true;
            controller.handleInstanceSelectionChange(controller.instances, controller.instances);
            expect(controller.availabilityZones.length).toEqual(1);
            expect(controller.availabilityZones[0].label).toEqual('one : 1 instances');
        });

        it('should select subnet when instance selected', function() {
            // set 2 subnets in model
            controller.vpcSubnetChoices = [
                {id:'subnet-10000001', label:'subnet1', labelBak:'subnet1'},
                {id:'subnet-10000002', label:'subnet2', labelBak:'subnet2'}
            ];
            controller.vpcSubnets = [];
            // select 1 instance
            controller.instances[0].selected = true;
            controller.handleInstanceSelectionChange(controller.instances, controller.instances);
            expect(controller.vpcSubnets.length).toEqual(1);
            expect(controller.vpcSubnets[0].label).toEqual('subnet1 : 1 instances');
        });
    });

    describe('Advanced tab controller', function () {

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/wizard/advanced.pt'];
            $templateCache.put('/_template/elbs/wizard/advanced', template);
        }));

        var $controller, $routeParams, controller;
        beforeEach(inject(function (_$controller_, _$routeParams_) {
            var $scope = $rootScope.$new();

            $controller = _$controller_;
            $routeParams = _$routeParams_;

            controller = $controller('AdvancedController', {
                $scope: $scope,
                $routeParams: $routeParams
            });
        }));

        it('should default the protocol value', function () {
            expect(controller.values.pingProtocol).toEqual('HTTP');
        });

        it('should default the port value', function () {
            expect(controller.values.pingPort).toEqual(80);
        });

        it('should default the path value', function () {
            expect(controller.values.pingPath).toEqual('/');
        });

        it('should default the response timeout', function () {
            expect(controller.values.responseTimeout).toEqual(5);
        });

        it('should default the time between pings', function () {
            expect(controller.values.timeBetweenPings).toEqual('30');
        });

        it('should default the failures until unhealthy', function () {
            expect(controller.values.failuresUntilUnhealthy).toEqual('2');
        });

        it('should default the passes until healthy', function () {
            expect(controller.values.passesUntilHealthy).toEqual('2');
        });

        it('should default the logging enabled ', function () {
            expect(controller.values.loggingEnabled).toEqual(false);
        });
    });
});

if (!Array.prototype.findIndex) {
  Object.defineProperty(Array.prototype, 'findIndex', {
    value: function(predicate) {
      'use strict';
      if (this === null) {
        throw new TypeError('Array.prototype.findIndex called on null or undefined');
      }
      if (typeof predicate !== 'function') {
        throw new TypeError('predicate must be a function');
      }
      var list = Object(this);
      var length = list.length >>> 0;
      var thisArg = arguments[1];
      var value;

      for (var i = 0; i < length; i++) {
        value = list[i];
        if (predicate.call(thisArg, value, i, list)) {
          return i;
        }
      }
      return -1;
    },
    enumerable: false,
    configurable: false,
    writable: false
  });
}
