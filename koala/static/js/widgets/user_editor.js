/**
 * @fileOverview User Editor JS
 * @requires AngularJS
 *
 */
angular.module('UserEditor', [])
    .controller('UserEditorCtrl', function ($scope) {
        $scope.userEditor = $('#user-editor');
        $scope.userInputs = $scope.userEditor.find('.userinput');
        $scope.usersTextarea = $scope.userEditor.find('textarea#users');
        $scope.usersArray = [];
        $scope.syncUsers = function () {
            var usersObj = {};
            $scope.usersArray.forEach(function(user) {
                usersObj[user.name] = user.email;
            });
            $scope.usersTextarea.val(JSON.stringify(usersObj));
        };
        $scope.initUsers = function() {
            console.log("we're initializing the user editor here!");
            $scope.syncUsers();
        };
        $scope.removeUser = function (index, $event) {
            $event.preventDefault();
            $scope.usersArray.splice(index, 1);
            $scope.syncUsers();
        };
        $scope.addUser = function ($event) {
            $event.preventDefault();
            var userEntry = $($event.currentTarget).closest('.userentry'),
                userNameField = userEntry.find('.name'),
                userEmailField = userEntry.find('.email'),
                usersArrayLength = $scope.usersArray.length,
                existingUserFound = false,
                form = $($event.currentTarget).closest('form'),
                invalidFields = form.find('[data-invalid]');
            if (userNameField.val() && userEmailField.val()) {
                // Trigger validation to avoid users that start with 'aws:'
                form.trigger('validate');
                if (invalidFields.length) {
                    invalidFields.focus();
                    return false;
                }
                // Avoid adding a new user if the name duplicates an existing one.
                for (var i=0; i < usersArrayLength; i++) {
                    if ($scope.usersArray[i].name === userNameField.val()) {
                        existingUserFound = true;
                        break;
                    }
                }
                if (existingUserFound) {
                    userNameField.focus();
                } else {
                    $scope.usersArray.push({
                        'name': userNameField.val(),
                        'email': userEmailField.val(),
                        'fresh': 'new'
                    });
                    $scope.syncUsers();
                    userNameField.val('').focus();
                    userEmailField.val('');
                }
            } else {
                userNameField.val() ? userEmailField.focus() : userNameField.focus();
            }
        };
    })
;
