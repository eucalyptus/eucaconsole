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
        $scope.displayBucketSharingChangeWarning = false;
        $scope.initS3SharingPanel = function (grants_json) {
            $scope.setInitialValues();
            $scope.initGrants(grants_json);
            $scope.grantsArray = JSON.parse(grants_json);
            $scope.initSharingPropagationWarning();
            $scope.addListeners();
        };
        $scope.setInitialValues = function () {
            $(document).ready(function () {
                $scope.$apply(function () {
                    $scope.shareType = $('input[name="share_type"]:checked').val()
                });
            });
        };
        $scope.initSharingPropagationWarning = function () {
            // Display warning when ACLs are modified on the bucket details page.
            var warningModal = $('#changed-sharing-warning-modal'),
                warningModalConfirmBtn = $('#confirm-changed-sharing-warning-modal-btn');
            // Modal exists only on bucket details page
            if (warningModal.length) {
                $scope.displayBucketSharingChangeWarning = true;
                $scope.$on('s3:sharingPanelAclUpdated', function () {
                    if ($scope.displayBucketSharingChangeWarning) {
                        warningModal.foundation('reveal', 'open');
                    }
                });
                // Prevent warning modal from displaying more than once per page
                warningModalConfirmBtn.on('click', function () {
                    warningModal.foundation('reveal', 'close');
                    $scope.$apply(function () {
                        $scope.displayBucketSharingChangeWarning = false;
                    });
                });
            }
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
            $('#share_permissions').val('FULL_CONTROL');
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
