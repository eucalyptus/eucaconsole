/**
 * @fileOverview Launch configurations landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('LaunchConfigsPage', ['LandingPage'])
    .controller('LaunchConfigsPageCtrl', function ($scope) {
        $scope.launchConfigName= '';
        $scope.launchConfigInUse = false;
        $scope.revealModal = function (action, launchConfig) {
            $scope.launchConfigName = launchConfig['name'];
            $scope.launchConfigInUse = launchConfig['in_use'];
            var modal = $('#' + action + '-launchconfig-modal');
            modal.foundation('reveal', 'open');
            setTimeout(function(){
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    if( inputElement != undefined ){
                        inputElement.focus()
                    }else{
                        modal.find('button').get(0).focus();
                    }
               }, 1000);
        };
    });

