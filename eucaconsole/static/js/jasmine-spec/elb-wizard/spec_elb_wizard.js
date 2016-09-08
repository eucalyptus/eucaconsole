/**
 * @fileOverview Jasmine Unit test for ELBWizard module.
 */

describe('ELBWizard', function () {
    
    beforeEach(angular.mock.module('ELBWizard'));

    var $compile, $rootScope, $templateCache;
    var template = '';

    beforeEach(angular.mock.inject(function (_$compile_, _$rootScope_, _$templateCache_) {
        $compile = _$compile_;
        $rootScope = _$rootScope_;
        $templateCache = $_templateCache_;
    }));
});
