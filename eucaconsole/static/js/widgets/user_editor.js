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
            return $scope.newUserName === '' || $scope.userEditor.$invalid;
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
        $scope.addUser = function () {
            var userNameField = $('#user-name-field');

            var existingUserFound = $scope.usersArray.some(function (user) {
                return user.name === $scope.newUserName;
            });
            if(existingUserFound) {
                userNameField.focus();
                return;
            }

            $scope.usersArray.push({
                name: $scope.newUserName,
                fresh: 'new'
            });
            $scope.syncUsers();
            $scope.newUserName = '';
            userNameField.focus();
            $scope.$emit('userAdded');
        };
    })
;
