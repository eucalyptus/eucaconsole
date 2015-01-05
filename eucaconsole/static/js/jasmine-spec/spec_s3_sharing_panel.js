/**
 * @fileOverview Jasmine Unittest for S3 Sharing Panel JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("S3SharingPanel", function() {

    beforeEach(angular.mock.module('S3SharingPanel'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('S3SharingPanelCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/panels/s3_sharing_panel.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of isNotValid is true", function() {
            expect(scope.isNotValid).toBeTruthy();
        });

        it("Initial value of shareType is empty", function() {
            expect(scope.shareType).toEqual('');
        });

        it("Initial value of aclType is manual", function() {
            expect(scope.aclType).toEqual('manual');
        });

        it("Initial value of addAccountBtnDisabled is true", function() {
            expect(scope.addAccountBtnDisabled).toBeTruthy();
        });

        it("Initial value of createOptionText is empty", function() {
            expect(scope.createOptionText).toEqual('');
        });

        it("Initial value of displayBucketSharingChangeWarning is false", function() {
            expect(scope.displayBucketSharingChangeWarning).not.toBeTruthy();
        });
    });

    describe("Function initS3SharingPanel() Test", function() {

        it("Should call setInitialValues() when initS3SharingPanel() is called", function() {
            spyOn(scope, 'setInitialValues');
            scope.initS3SharingPanel('{}');
            expect(scope.setInitialValues).toHaveBeenCalled();
        });
    });
});
