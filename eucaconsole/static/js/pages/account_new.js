/**
 * @fileOverview IAM Create Account Page JS
 * @requires AngularJS
 *
 */

angular.module('AccountPage', [])
    .controller('AccountPageCtrl', function ($scope, $http, $timeout) {
        $scope.submitEndpoint = '';
        $scope.accountRedirect = '';
        $scope.accountName = '';
        $scope.isNotValid = true;
        $scope.initController = function (submitEndpoint, redirectEndpoint, getFileEndpoint) {
            $scope.submitEndpoint = submitEndpoint;
            $scope.accountRedirect = redirectEndpoint;
            $scope.getFileEndpoint = getFileEndpoint;
            $scope.setWatch();
        };
        $scope.submit = function($event) {
            var form = $($event.target);
            var csrf_token = form.find('input[name="csrf_token"]').val();
            var data = $($event.target).serialize();
            //$scope.accountName = form.find('input[name="account-name"]').val();
            $http({method:'POST', url:$scope.submitEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                Notify.success(oData.message);
                if (results.hasFile == 'y') {
                    /*
                    $.generateFile({
                        csrf_token: csrf_token,
                        filename: 'not-used', // let the server set this
                        content: 'none',
                        script: $scope.getFileEndpoint
                    });
                    */
                    // this is clearly a hack. We'd need to bake callbacks into the generateFile
                    // stuff to do this properly.
                    setTimeout(function() {
                        window.location = $scope.accountRedirect.replace('_name_', $scope.accountName);
                    }, 3000);
                }
            });
        };
        $scope.setWatch = function () {
            $scope.$watch('accountName' , function () {
                if( $scope.accountName === '' || $scope.accountName === undefined ){
                    $scope.isNotValid = true;
                }else{
                    $scope.isNotValid = false;
                }
            });
        };
    })
;



