/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for IAM Bucket Details JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("BucketDetailsPage", function() {

    beforeEach(angular.mock.module('BucketDetailsPage'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('BucketDetailsPageCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/buckets/bucket_details.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Tests", function() {

        it("Initial value of isSubmitted is false", function() {
            expect(scope.isSubmitted).not.toBeTruthy();
        });

        it("Initial value of hasChangesToBeSaved is false", function() {
            expect(scope.hasChangesToBeSaved).not.toBeTruthy();
        });

        it("Initial value of objectsCountLoading is true", function() {
            expect(scope.objectsCountLoading).toBeTruthy();
        });

        it("Initial value of hasCorsConfig is false", function() {
            expect(scope.hasCorsConfig).toBe(false);
        });

        it("Initial value of savingCorsConfig is false", function() {
            expect(scope.savingCorsConfig).toBe(false);
        });

        it("Initial value of deletingCorsConfig is false", function() {
            expect(scope.deletingCorsConfig).toBe(false);
        });

    });

    describe("Function initController() Tests", function() {
        var optionsJson = '{"bucket_objects_count_url": "objects_count_url", "has_cors_config": false}';

        it("Should set bucketObjectsCountUrl when initController() is called", function() {
            scope.initController(optionsJson);
            expect(scope.bucketObjectsCountUrl).toEqual('objects_count_url');
        });

        it("Should set hasCorsConfig boolean when controller is initialized", function() {
            scope.initController(optionsJson);
            expect(scope.hasCorsConfig).toBe(false);
        });

        it("Should call handleUnsavedChanges() when initController() is called", function() {
            spyOn(scope, 'handleUnsavedChanges');
            scope.initController('{}');
            expect(scope.handleUnsavedChanges).toHaveBeenCalled();
        });
    });

    describe("CORS Config save event Test", function() {
        it("Should set hasCorsConfig to after CORS config is saved", function() {
            scope.$broadcast('s3:corsConfigSaved');
            expect(scope.hasCorsConfig).toBe(true);
        });

    });
});


describe("CORS Configuration Modal Directive", function() {

    beforeEach(angular.mock.module('BucketDetailsPage'));

    var $compile, $rootScope, $templateCache, $httpBackend, element, scope;
    var template = window.__html__['templates/dialogs/bucket_cors_configuration_dialog.pt'];

    beforeEach(angular.mock.inject(function (_$compile_, _$rootScope_, _$templateCache_) {
        $compile = _$compile_;
        $rootScope = _$rootScope_;
        $templateCache = _$templateCache_;

        $templateCache.put('mock.template.html', template);
    }));

    beforeEach(angular.mock.inject(function ($injector) {
        $httpBackend = $injector.get('$httpBackend');
        $httpBackend.when('GET', '/static/json/routes.json').respond(200, '');
    }));

    beforeEach(function () {
        var directiveHtml = [
            '<div cors-config-modal=""',
            'template="mock.template.html"',
            'has-cors-config="false"',
            'cors-config-xml=""',
            'sample-cors-config="<CORSConfiguration><CORSRule></CORSRule></CORSConfiguration>"',
            '></div>'
        ].join('');
        element = $compile(directiveHtml)($rootScope);
        $rootScope.$digest();
        $httpBackend.flush();
        scope = element.isolateScope();
    });

    it('should default hasCorsConfig to false', function () {
        expect(scope.hasCorsConfig).toBe(false);
    });

    it('should display Add CORS Configuration in modal dialog when no existing CORS config', function () {
        expect(element.find('h3 span').text()).toEqual('Add CORS Configuration');
    });


});
