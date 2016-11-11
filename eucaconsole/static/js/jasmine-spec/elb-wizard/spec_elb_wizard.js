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

        var ELBWizardService;

        beforeEach(angular.mock.inject(function (_ELBWizardService_) {
            ELBWizardService = _ELBWizardService_;
        }));

        describe('the service', function () {

            it('should default certsAvailable', function () {
                expect(ELBWizardService.certsAvailable).toEqual([]);
            });

            it('should default policies', function () {
                expect(ELBWizardService.policies).toEqual([]);
            });
        });

        describe('#validSteps', function () {

            it('should return the appropriate number of steps for euca, non-vpc clouds', function () {
                var nav = ELBWizardService.validSteps('euca', false);
                expect(nav.steps.length).toEqual(3);
            });

            it('should return the appropriate number of steps for euca, vpc clouds', function () {
                var nav = ELBWizardService.validSteps('euca', true);
                expect(nav.steps.length).toEqual(4);
            });

            it('should return the appropriate number of steps for aws clouds', function () {
                var nav = ELBWizardService.validSteps('aws');
                expect(nav.steps.length).toEqual(4);
            });
        });

        describe('#next', function () {

            var nav, current;

            beforeEach(function () {
                nav = ELBWizardService.validSteps('euca', true);
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
                '<wizard-nav cloud-type="euca"></wizard-nav>'
            )($rootScope);
            $rootScope.$digest();

            scope = element.isolateScope();

            $location.path('/elbs/wizard/');
            $rootScope.$apply();

            controller = element.controller('wizardNav');
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
            expect(controller.listeners.length).toEqual(1);
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

        it('should certainly do something');
    });

    describe('Instances tab controller', function () {

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/wizard/instances.pt'];
            $templateCache.put('/_template/elbs/wizard/instances', template);
        }));

        var $controller, $routeParams, controller;
        beforeEach(inject(function (_$controller_, _$routeParams_) {
            var $scope = $rootScope.$new();

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
        });

        it('should deselect instance', function() {
            // select 1 from each zone
            controller.instances[0].selected = true;
            controller.instances[2].selected = true;
            // set 2 zones in model
            var zones = [
                {id:'one', label:'one'},
                {id:'two', label:'two'}
            ];
            controller.handleDeselectionDueToZones([zones[0]], zones);
            expect(controller.instances[0].selected).toBe(true);
            expect(controller.instances[1].selected).toBe(false);
            expect(controller.instances[2].selected).toBe(false);
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
            expect(controller.protocol).toEqual('HTTP');
        });

        it('should default the port value', function () {
            expect(controller.port).toEqual(80);
        });

        it('should default the path value', function () {
            expect(controller.path).toEqual('/');
        });
    });
});
