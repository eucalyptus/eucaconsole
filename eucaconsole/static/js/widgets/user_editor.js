/**
 * @fileOverview User Editor JS
 * @requires AngularJS
 *
 */
angular.module('UserEditor', [])
    .controller('UserEditorCtrl', function ($scope, $timeout) {
        $scope.userEditor = $('#user-editor');
        $scope.userInputs = $scope.userEditor.find('.userinput');
        $scope.usersTextarea = $scope.userEditor.find('textarea#users');
        $scope.isDisabled = true;
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
            $scope.setWatch();
        };
        $scope.setWatch = function () {
            $scope.$watch('newUserName', function () {
                $scope.validateUsername();
            });
        };
        $scope.removeUser = function (index, $event) {
            $event.preventDefault();
            $scope.usersArray.splice(index, 1);
            $scope.syncUsers();
            if( $scope.usersArray.length == 0 ){
                $scope.$emit('emptyUsersArray');
            }
        };
        $scope.keyListener = function ($event) {
            if ($event.keyCode == 13) {
                $scope.addUser($event)
            }
        };
        $scope.validateUsername = function ($event) {
           if( $scope.newUserName.match(/^[a-zA-Z0-9\+\=\,\.\@\-]{1,64}$/) ){
               $scope.isDisabled = false;
           }else {
               $scope.isDisabled = true;
           }
        }
        $scope.addUser = function ($event) {
            $event.preventDefault();
            $scope.validateUsername();
            if( $scope.isDisabled ){
                return false;
            }
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
                    $scope.isDisabled = true;
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
                    $scope.isDisabled = true;
                } else {
                    $scope.usersArray.push({
                        'name': $scope.newUserName,
                        'fresh': 'new'
                    });
                    $scope.syncUsers();
                    $scope.newUserName = '';
                    userNameField.val('').focus();
                    $scope.isDisabled = true;
                    $scope.$emit('userAdded');
                }
            } else {
                userNameField.focus();
                $scope.isDisabled = true;
            }
        };
    })
;
