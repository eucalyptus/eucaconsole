/**
 * @fileOverview S3 Sharing Panel JS
 * @requires AngularJS
 *
 */
angular.module('S3SharingPanel', [])
    .controller('S3SharingPanelCtrl', function ($scope) {
        $scope.s3AclTextarea = $('#s3-sharing-acl');
        $scope.sharingAccountList = [];
        $scope.isNotValid = true;
        $scope.grantsArray = [];
        $scope.shareType = '';
        $scope.initS3SharingPanel = function (grants_json) {
            $scope.setInitialValues();
            $scope.initGrants(grants_json);
            $scope.grantsArray = JSON.parse(grants_json);
            $scope.addListeners();
        };
        $scope.setInitialValues = function () {
            $(document).ready(function () {
                $scope.$apply(function () {
                    $scope.shareType = $('input[name="share_type"]:checked').val()
                });
            });
        };
        $scope.addListeners = function () {
            $(document).ready(function() {
                $('input[name="share_type"]').on('change', function() {
                    $scope.$apply(function () {
                        $scope.shareType = $('input[name="share_type"]:checked').val();
                    });
                });
            });
        };
        $scope.initGrants = function(grantsJson) {
            $scope.s3AclTextarea.val(grantsJson);
            // Parse grants JSON and convert to a list of grants.
            grantsJson = grantsJson.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
            $scope.grantsArray = JSON.parse(grantsJson);
        };
        $scope.syncGrants = function() {
            $scope.s3AclTextarea.val(JSON.stringify($scope.grantsArray));
            $scope.$emit('s3:sharingPanelAclUpdated');
        };
        $scope.removeGrant = function (index, $event) {
            $event.preventDefault();
            $scope.grantsArray.splice(index, 1);
            $scope.syncGrants();
        };
    })
;
