/**
 * @fileOverview S3 Sharing Panel JS
 * @requires AngularJS
 *
 */
angular.module('S3SharingPanel', ['EucaConsoleUtils'])
    .controller('S3SharingPanelCtrl', function ($scope, eucaUnescapeJson) {
        $scope.s3AclTextarea = $('#s3-sharing-acl');
        $scope.sharingAccountList = [];
        $scope.isNotValid = true;
        $scope.grantsArray = [];
        $scope.shareType = '';
        $scope.aclType = 'manual';
        $scope.addAccountBtnDisabled = true;
        $scope.displayBucketSharingChangeWarning = false;
        $scope.initS3SharingPanel = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            var grantsList = options['grants'];
            var grantsJson = JSON.stringify(grantsList);
            $scope.grantsArray = grantsList;
            $scope.s3AclTextarea.val(grantsJson);
            $scope.setInitialValues();
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
        $scope.syncGrants = function() {
            $scope.s3AclTextarea.val(JSON.stringify($scope.grantsArray));
            $scope.$emit('s3:sharingPanelAclUpdated');
            // Reset form values
            $('#share_account').val('');
            $('#share_permissions').val('FULL_CONTROL');
        };
        $scope.removeGrant = function (index, $event) {
            $event.preventDefault();
            $scope.grantsArray.splice(index, 1);
            $scope.syncGrants();
        };
        $scope.addGrant = function ($event) {
            $event.preventDefault();
            var grantEntry = $($event.currentTarget).closest('#sharing-acls'),
                grantAccountField = grantEntry.find('#share_account'),
                grantPermissionField = grantEntry.find('#share_permissions'),
                grantAccountVal = grantAccountField.val(),
                grantPermVal = grantPermissionField.val(),
                existingGrantFound = false;
            if (grantAccountVal && grantPermVal) {
                var newGrant = {
                    'permission': grantPermVal,
                    'grant_type': 'CanonicalUser'
                };
                angular.forEach($scope.grantsArray, function (grant) {
                    var idPermMatches = grant.id == grantAccountVal && grant.permission == grantPermVal;
                    var emailPermMatches = grant.email_address == grantAccountVal && grant.permission == grantPermVal;
                    if (idPermMatches || emailPermMatches) {
                        existingGrantFound = true;
                    }
                    // Detect if entered account is an ID or email
                    if (grantAccountVal.match('@')) {
                        newGrant['email_address'] = grantAccountVal;
                    } else {
                        newGrant['id'] = grantAccountVal;
                    }
                });
                // Focus on account input if existing grant found (matched by id/permission or email/permission above)
                if (existingGrantFound) {
                    grantAccountField.focus();
                    return false;
                }
                $scope.grantsArray.push(newGrant);
                $scope.syncGrants();
                $scope.addAccountBtnDisabled = true;
            } else {
                grantAccountField.val() ? grantPermissionField.focus() : grantAccountField.focus();
            }
        };
    })
;
