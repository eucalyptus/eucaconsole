/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview IAM Create Role Page JS
 * @requires AngularJS
 *
 */

angular.module('RolePage', [])
    .controller('RolePageCtrl', function ($scope, $timeout) {
        $scope.roleType = "ec2";
        $scope.initController = function (all_users) {
            $scope.$watch('roleType', function() {
                if ($scope.roleType == "ec2") {
                    $("#accountid").removeAttr("required");
                }
                else {
                    $("#accountid").attr("required", "required");
                }
            });
        };
    })
;



