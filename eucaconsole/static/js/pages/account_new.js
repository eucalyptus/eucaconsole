/**
 * @fileOverview IAM Create Account Page JS
 * @requires AngularJS
 *
 */

var validateAccountAlias = (function () {
    var aliasPattern = /^[a-z0-9][a-z0-9\.@\-]{1,61}[a-z0-9]$/;
    var iamAcctAntiPattern = /^[0-9]{12}$/;

    return function (alias) {
        // Fail on match of iam account number
        if(iamAcctAntiPattern.test(alias)) {
            return false;
        }

        // Pass on match of alias pattern
        if(aliasPattern.test(alias)) {
            return true;
        }

        return false;
    };
})();

$(document).foundation({
    abide: {
        validators: {
            accountAlias: function (el) {
                return validateAccountAlias(el.value);
            }
        }
    }
});

// New user page includes the User Editor editor
angular.module('CreateAccountPage', ['UserEditor', 'Quotas', 'EucaConsoleUtils'])
    .controller('CreateAccountPageCtrl', function ($scope, $http, $timeout, eucaHandleError) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.submitEndpoint = '';
        $scope.accountRedirect = '';
        $scope.accountName = '';
        $scope.quotas_expanded = false;
        $scope.isNotValid = true;
        $scope.initController = function (submitEndpoint, redirectEndpoint, getFileEndpoint) {
            $scope.submitEndpoint = submitEndpoint;
            $scope.accountRedirect = redirectEndpoint;
            $scope.getFileEndpoint = getFileEndpoint;
            $scope.setWatch();
        };
        $scope.toggleQuotasContent = function () {
            $scope.quotas_expanded = !$scope.quotas_expanded;
        };
        $scope.submit = function($event) {
            $('#quota-error').css('display', 'none');
            var form = $($event.target);
            var invalid = form.find('input[data-invalid]');
            if (invalid.length > 0) {
                $('#quota-error').css('display', 'block');
                return false;
            }
            var csrf_token = form.find('input[name="csrf_token"]').val();
            var data = $($event.target).serialize();
            //$scope.accountName = form.find('input[name="account-name"]').val();
            $http({method:'POST', url:$scope.submitEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                Notify.success(oData.message);
                if (results.hasFile == 'y') {
                    $.generateFile({
                        csrf_token: csrf_token,
                        filename: 'not-used', // let the server set this
                        content: 'none',
                        script: $scope.getFileEndpoint
                    });
                    // this is clearly a hack. We'd need to bake callbacks into the generateFile
                    // stuff to do this properly.
                    setTimeout(function() {
                        window.location = $scope.accountRedirect.replace('_name_', $scope.accountName);
                    }, 3000);
                }
              }).
              error(function(oData, status) {
                eucaHandleError(oData, status);
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
    .directive('accountAlias', function () {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, elem, attrs, ctrl) {
                ctrl.$validators.accountAlias = function (modelVal, viewVal) {
                    return validateAccountAlias(viewVal);
                };
            }
        };
    })
;



