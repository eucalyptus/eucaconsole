/**
 * @fileOverview User Editor JS
 * @requires AngularJS
 *
 */
angular.module('UserEditor', [])
    .directive('reserved', function () {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                var reserved = attrs.reserved.split(/\s+/);
                ctrl.$validators.reserved = function (modelValue) {
                    var isValid = reserved.indexOf(modelValue) === -1;
                    return isValid;
                };
            }
        };
    })
    .controller('UserEditorCtrl', function ($scope) {
        $scope.isDisabled = function () {
            return $scope.userEditor.$invalid;
        };
        $scope.usersTextarea = $('#user-editor').find('textarea#users');
        $scope.newUserName = '';
        $scope.usersArray = [];
        $scope.syncUsers = function () {
            var usersObj = {};
            $scope.usersArray.forEach(function(user) {
                usersObj[user.name] = "no-email"; //user.email;
            });
            $scope.usersTextarea.val(JSON.stringify(usersObj));
        };
        $scope.initUsers = function() {
            $scope.syncUsers();
        };
        $scope.removeUser = function (index, $event) {
            $event.preventDefault();
            $scope.usersArray.splice(index, 1);
            $scope.syncUsers();
            if( $scope.usersArray.length === 0 ){
                $scope.$emit('emptyUsersArray');
            }
        };
        $scope.keyListener = function ($event) {
            if ($event.keyCode == 13) {
                $scope.addUser($event);
            }
        };
        $scope.addUser = function ($event) {
            $event.preventDefault();
            var userEntry = $($event.currentTarget).closest('.userentry'),
                userNameField = userEntry.find('.name'),
                usersArrayLength = $scope.usersArray.length,
                existingUserFound = false,
                form = $($event.currentTarget).closest('form'),
                invalidFields = form.find('[data-invalid]');
            if (userNameField.val()) {
                // Trigger validation to avoid users that start with 'aws:'
                form.trigger('validate');
                if (invalidFields.length) {
                    invalidFields.focus();
                    return false;
                }
                // Avoid adding a new user if the name duplicates an existing one.
                for (var i=0; i < usersArrayLength; i++) {
                    if ($scope.usersArray[i].name === $scope.newUserName) {
                        existingUserFound = true;
                        break;
                    }
                }
                if (existingUserFound) {
                    userNameField.focus();
                } else {
                    $scope.usersArray.push({
                        'name': $scope.newUserName,
                        'fresh': 'new'
                    });
                    $scope.syncUsers();
                    $scope.newUserName = '';
                    userNameField.val('').focus();
                    $scope.$emit('userAdded');
                }
            } else {
                userNameField.focus();
            }
        };
    })
;
