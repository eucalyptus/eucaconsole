/**
 * @fileOverview Jasmine Unittest for Create Alarm JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("CreateAlarm", function() {

    beforeEach(angular.mock.module('CreateAlarm'));

    var scope, ctrl;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('CreateAlarmCtrl', {
            $scope: scope
        });
    }));

    beforeEach(function() {
        var template = window.__html__['templates/dialogs/create_alarm_dialog.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/\<link/g, "\<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("Initial value of metric is empty", function() {
            expect(scope.metric).toEqual('');
        });

        it("Initial value of unitLabel is empty", function() {
            expect(scope.unitLabel).toEqual('');
        });

        it("Initial value of isCreatingAlarms is false", function() {
            expect(scope.isCreatingAlarms).not.toBeTruthy();
        });

        it("Initial value of alarmName is empty", function() {
            expect(scope.alarmName).toEqual('');
        });

        it("Initial value of existingAlarmConflict is false", function() {
            expect(scope.existingAlarmConflict).not.toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should set metricUnitMapping when initController() is called and metric_unit_mapping JSON is set", function() {
            scope.initController('{"metric_unit_mapping": "metric"}');
            expect(scope.metricUnitMapping).toEqual('metric');
        });

        it("Should call addListeners() when initController() is called", function() {
            spyOn(scope, 'addListeners');
            scope.initController('{}');
            expect(scope.addListeners).toHaveBeenCalled();
        });
    });
});
