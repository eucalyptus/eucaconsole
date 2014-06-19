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
           }else{
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
                //userEmailField = userEntry.find('.email'),
                usersArrayLength = $scope.usersArray.length,
                existingUserFound = false,
                form = $($event.currentTarget).closest('form'),
                invalidFields = form.find('[data-invalid]');
            if (userNameField.val()) {// && userEmailField.val()) {
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
                        //'email': userEmailField.val(),
                        'fresh': 'new'
                    });
                    $scope.syncUsers();
                    $scope.isDisabled = true;
                    $scope.newUserName = '';
                    userNameField.val('').focus();
                    $scope.isDisabled = true;
                    //userEmailField.val('');
                    $scope.$emit('userAdded');
                }
            } else {
                //userNameField.val() ? userEmailField.focus() : userNameField.focus();
                userNameField.focus();
            }
        };
    })
;
