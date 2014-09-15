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
        $scope.aclType = 'manual';
        $scope.addAccountBtnDisabled = true;
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
                // Set appropriate share type value
                $('input[name="share_type"]').on('change', function() {
                    $scope.$apply(function () {
                        $scope.shareType = $('input[name="share_type"]:checked').val();
                        $scope.$emit('s3:sharingPanelAclUpdated');
                    });
                });
                $('input[name="acl_type"]').on('change', function() {
                    $scope.$apply(function () {
                        $scope.$emit('s3:sharingPanelAclUpdated');
                    });
                });
                // Disable Add Account button if account ID input is empty
                $('#share_account').on('keyup', function () {
                    var that = $(this);
                    $scope.$apply(function () {
                        $scope.addAccountBtnDisabled = that.val() == '';
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
            // Reset form values
            $('#share_account').val('');
            $('#share_permissions').val('READ');
        };
        $scope.removeGrant = function (index, $event) {
            $event.preventDefault();
            $scope.grantsArray.splice(index, 1);
            $scope.syncGrants();
        };
        $scope.addGrant = function ($event) {
            $event.preventDefault();
            var grantEntry = $($event.currentTarget).closest('#sharing-private'),
                grantAccountField = grantEntry.find('#share_account'),
                grantPermissionField = grantEntry.find('#share_permissions'),
                grantAccountVal = grantAccountField.val(),
                grantPermVal = grantPermissionField.val(),
                existingGrantFound = false;
            if (grantAccountVal && grantPermVal) {
                // Skip if existing grant found
                angular.forEach($scope.grantsArray, function (grant) {
                    if (grant.id == grantAccountVal && grant.permission == grantPermVal) {
                        existingGrantFound = true;
                    }
                });
                if (existingGrantFound) {
                    grantAccountField.focus();
                    return false;
                }
                $scope.grantsArray.push({
                    'id': grantAccountVal,
                    'permission': grantPermVal,
                    'grant_type': 'CanonicalUser'
                });
                $scope.syncGrants();
            } else {
                grantAccountField.val() ? grantPermissionField.focus() : grantAccountField.focus();
            }
        };
    })
;
