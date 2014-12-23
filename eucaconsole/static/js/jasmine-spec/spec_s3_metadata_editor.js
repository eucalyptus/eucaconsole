/**
 * @fileOverview Jasmine Unittest for S3 Metadata Editor JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("S3MetadataEditor", function() {

    beforeEach(angular.mock.module('S3MetadataEditor'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('S3MetadataEditorCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/panels/s3_metadata_editor.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of newMetadataKey is empty", function() {
            expect(scope.newMetadataKey).toEqual('');
        });

        it("Initial value of newMetadataValue is empty", function() {
            expect(scope.newMetadataValue).toEqual('');
        });

        it("Initial value of newMetadataContentType is empty", function() {
            expect(scope.newMetadataContentType).toEqual('');
        });

        it("Initial value of addMetadataBtnDisabled is true", function() {
            expect(scope.addMetadataBtnDisabled).toBeTruthy();
        });
    });

    describe("Function initMetadata() Test", function() {

        it("Should call syncMetadata() when initMetadata() is called", function() {
            spyOn(scope, 'syncMetadata');
            scope.initMetadata('{}', 'a', 'b');
            expect(scope.syncMetadata).toHaveBeenCalled();
        });

        it("Value of metadataKeyOptionText is updated when initMetadata() is called", function() {
            scope.metadataKeyOptionText = '';
            scope.initMetadata('{}', 'b', 'c');
            expect(scope.metadataKeyOptionText).toEqual('b');
        });

        it("Value of metadataKeyNoResultsText is updated when initMetadata() is called", function() {
            scope.metadataKeyNoResultsText = '';
            scope.initMetadata('{}', 'b', 'c');
            expect(scope.metadataKeyNoResultsText).toEqual('c');
        });
    });
});
