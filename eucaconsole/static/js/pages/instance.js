/**
 * @fileOverview Instance page JS
 * @requires AngularJS
 *
 */

// Instance page includes the tag editor, so pull in that module as well.
angular.module('InstancePage', ['TagEditor'])
    .controller('InstancePageCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.instanceStateEndpoint = '';
        // Valid instance states are: "pending", "running", "shutting-down", "terminated", "stopping", "stopped"
        // 'shutting-down' = terminating state
        $scope.transitionalStates = ['pending', 'stopping', 'shutting-down'];
        $scope.instanceState = '';
        $scope.isUpdating = false;
        $scope.isNotStopped = $scope.instanceState != 'stopped';
        $scope.instanceForm = $('#instance-form');
        $scope.isTransitional = function (state) {
            return $scope.transitionalStates.indexOf(state) !== -1;
        };
        $scope.initController = function (jsonEndpoint, ipaddressEndpoint, consoleEndpoint, state, id, name, group_name, key_name, public_ip, public_dns_name, platform, has_elastic_ip) {
            $scope.instanceStateEndpoint = jsonEndpoint;
            $scope.instanceIPAddressEndpoint = ipaddressEndpoint;
            $scope.consoleOutputEndpoint = consoleEndpoint;
            $scope.instanceState = state;
            $scope.instanceID = id;
            $scope.instance_name = name;
            $scope.groupName = group_name;
            $scope.keyName = key_name;
            $scope.instancePublicIP = public_ip;
            $scope.publicDNS = public_dns_name;
            $scope.platform = platform;
            $scope.hasElasticIP = Boolean(has_elastic_ip.toLowerCase());
            $scope.getInstanceState();
            $scope.activateWidget();
            $scope.setWatch();
            $scope.setFocus();
            $('#file').on('change', $scope.getPassword);
        };
        $scope.activateWidget = function () {
            $('#associate-ip-to-instance-modal').on('open', function(){
                var thisSelect = $(this).find('#ip_address');
                thisSelect.chosen({'width': '80%', 'search_contains': true});
            });
        };
        $scope.revealConsoleOutputModal = function() {
            $('.actions-menu').trigger('click');
            $http.get($scope.consoleOutputEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.consoleOutput = results;
                    var modal = $('#console-output-modal');
                    modal.foundation('reveal', 'open');
                }
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
            });
        };
        $scope.setFocus = function () {
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if( modalID.match(/terminate/)  || modalID.match(/delete/) || modalID.match(/release/) ){
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                }else{
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement) {
                        inputElement.focus();
                    } else if (!!modalButton) {
                        modalButton.focus();
                    }
               }
            });
        };
        $scope.setWatch = function () {
            $scope.$watch('instanceState', function(){
                $scope.getIPAddressData();
            });
        };
        $scope.getIPAddressData = function () {
            $http.get($scope.instanceIPAddressEndpoint).success(function(oData) {
                $scope.instancePublicIP = oData ? oData.ip_address : '';
                $scope.PublicDNS = oData ? oData.public_dns_name : '';
                $scope.instancePrivateIP = oData ? oData.private_ip_address : '';
                $scope.PrivateDNS = oData ? oData.private_dns_name : '';
                $scope.hasElasticIP = oData ? oData.has_elastic_ip : '';
            });
        };
        $scope.getInstanceState = function () {
            $http.get($scope.instanceStateEndpoint).success(function(oData) {
                $scope.instanceState = oData ? oData.results : '';

                // Poll to obtain desired end state if current state is transitional
                if ($scope.isTransitional($scope.instanceState)) {
                    $scope.isUpdating = true;
                    $timeout(function() {$scope.getInstanceState()}, 4000);  // Poll every 4 seconds
                } else {
                    $scope.isUpdating = false;
                }
                $scope.isNotStopped = $scope.instanceState != 'stopped';
            });
        };
        $scope.submitSaveChanges = function($event){
            $event.preventDefault();
            if( $scope.instanceState == 'stopped' ){
                $('#update-instance-modal').foundation('reveal', 'open');
            }else{
                $scope.instanceForm.submit();
            }
        };
        $scope.submitUpdateInstance = function ($event) {
            $event.preventDefault();
            $('a.close-reveal-modal').trigger('click');
            $('#start_later').val('true');
            $scope.instanceForm.submit();
        };
        $scope.cancelUpdateInstance = function ($event) {
            $event.preventDefault();
            $('a.close-reveal-modal').trigger('click');
            $scope.instanceForm.submit();
        };
        $scope.promptFile = function (url) {
            $('#file').trigger('click');
            $scope.password_url = url;
        };
        $scope.getPassword = function (evt) {
            $('#file').attr('display', 'none');
            var file = evt.target.files[0];
            var reader = new FileReader();
            reader.onloadend = function(evt) {
                if (evt.target.readyState == FileReader.DONE) {
                    var key_contents = evt.target.result;
                    var url = $scope.password_url.replace("_id_", $scope.instanceID);
                    var data = "csrf_token=" + $('#csrf_token').val() + "&key=" + $.base64.encode(key_contents);
                    $http({method:'POST', url:url, data:data,
                           headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                      success(function(oData) {
                        var results = oData ? oData.results : [];
                        $('#the-password').text(results.password);
                      }).
                      error(function (oData, status) {
                        if (status == 403) window.location = '/';
                        var errorMsg = oData['message'] || '';
                        Notify.failure(errorMsg);
                      });
                }
            }
            reader.readAsText(file);
        }
    })
;

