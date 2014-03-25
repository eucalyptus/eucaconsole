/**
 * @fileOverview Instances landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('InstancesPage', ['LandingPage'])
    .controller('InstancesCtrl', function ($scope, $http) {
        $scope.instanceID = '';
        $scope.fileName = '';
        $scope.batchTerminateModal = $('#batch-terminate-modal');
        $scope.associateIPModal = $('#associate-ip-to-instance-modal');
        $scope.initChosenSelectors = function () {
            $scope.batchTerminateModal.on('open', function () {
                var instanceIdsSelect = $scope.batchTerminateModal.find('select');
                instanceIdsSelect.chosen({'width': '100%', 'search_contains': true});
                instanceIdsSelect.trigger('chosen:updated');
            });
            $scope.associateIPModal.on('open', function () {
                $('#ip_address').chosen({'width': '80%'});
                $('#ip_address').trigger('chosen:updated');
            });
        };
        $scope.initController = function () {
            $scope.initChosenSelectors();
            $('#file').on('change', $scope.getPassword);
        };
        $scope.revealModal = function (action, instance) {
            var modal = $('#' + action + '-instance-modal');
            $scope.instanceID = instance['id'];
            $scope.instanceName = instance['name'];
            $scope.rootDevice = instance['root_device'];
            $scope.groupName = instance['security_groups'][0].name;
            $scope.keyName = instance['key_name'];
            $scope.publicDNS = instance['public_dns_name'];
            $scope.platform = instance['platform'];
            $scope.ipAddress = instance['ip_address'];
            modal.foundation('reveal', 'open');
        };
        $scope.unterminatedInstancesCount = function (items) {
            return items.filter(function (item) {
                return item.status !== 'terminated';
            }).length;
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
        };
        $scope.revealConsoleOutputModal = function(instance) {
            $(document).trigger('click');
            $scope.instanceName = instance['name'];
            var consoleOutputEndpoint = "/instances/" + instance['id'] + "/consoleoutput/json";
            $http.get(consoleOutputEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.consoleOutput = results;
                    var modal = $('#console-output-modal');
                    modal.foundation('reveal', 'open');
                }
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
    })
;

