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

    describe('wizardNav directive', function () {

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/wizard/navigation.pt'];
            $templateCache.put('/_template/elbs/wizard/navigation', template);
        }));

        describe('with cloud-type == "euca"', function () {

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

            it('should have the appropriate number of tabs', function () {
                var tabItems = element.find('dd');
                expect(tabItems.length).toEqual(3);
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

            it('should navigate to the appropriate url when a tab is clicked');

            it('should not allow navigation to disabled tabs');

            it('should allow navigation to enabled tabs');
        });

        describe('with cloud-type == "euca" and vpc enabled', function () {

            var element, scope;
            beforeEach(function () {
                element = $compile(
                    '<wizard-nav cloud-type="euca" vpc-enabled="1"></wizard-nav>'
                )($rootScope);
                $rootScope.$digest();

                scope = element.isolateScope();
            });

            it('should have the appropriate number of tabs', function () {
                var tabItems = element.find('dd');
                expect(tabItems.length).toEqual(4);
            });
        });

        describe('with cloud-type == "aws"', function () {

            var element, scope;
            beforeEach(function () {
                element = $compile(
                    '<wizard-nav cloud-type="aws" vpc-enabled=""></wizard-nav>'
                )($rootScope);
                $rootScope.$digest();

                scope = element.isolateScope();
            });
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

        var element, scope;

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/wizard/general.pt'];
            $templateCache.put('/_template/elbs/wizard/general', template);
        }));

        var $controller, $routeParams, $location, controller;
        beforeEach(inject(function (_$controller_, _$routeParams_, _$location_) {
            scope = $rootScope.$new();

            $controller = _$controller_;
            $routeParams = _$routeParams_;
            $location = _$location_;

            controller = $controller('GeneralController', {
                $scope: scope,
                $routeParams: $routeParams,
                $location: $location
            });
        }));

        it('should add one default listener', function () {
            expect(controller.listeners.length).toEqual(1);
        });

        describe('#submit', function () {

            beforeEach(function () {
                scope.generalForm = {};

                $location.path('/elbs/wizard/');
                $rootScope.$apply();
            });

            it('should move to next step on submit when valid', function () {
                scope.generalForm.$invalid = false;

                controller.submit();
                expect($location.path()).toEqual('/elbs/wizard/instances');
            });

            it('should not move to next step on submit when invalid', function () {
                scope.generalForm.$invalid = true;

                controller.submit();
                expect($location.path()).toEqual('/elbs/wizard/');
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

        it('should certainly do something');
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

        it('should certainly do something');
    });
});
