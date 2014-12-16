/**
 * @fileOverview Jasmine Unittest for Image Picker JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("ImagePicker", function() {

    beforeEach(angular.mock.module('ImagePicker'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('ImagePickerCtrl', {
            $scope: scope
        });
    }));

    describe("Initial Values Test", function() {

        it("Initial value of batchSize is 100", function() {
            expect(scope.batchSize).toEqual(100);
        });

        it("Initial value of ownerAlias is empty", function() {
            expect(scope.ownerAlias).toEqual('');
        });

        it("Initial value of itemsLoading is false", function() {
            expect(scope.itemsLoading).not.toBeTruthy();
        });

        it("Initial value of cloudType is euca", function() {
            expect(scope.cloudType).toEqual('euca');
        });
    });

    describe("Function initImagePicker() Test", function() {

        it("Should call getItems() when initImagePicker() is called", function() {
            spyOn(scope, 'getItems');
            scope.initImagePicker('{}');
            expect(scope.getItems).toHaveBeenCalled();
        });
    });
});
