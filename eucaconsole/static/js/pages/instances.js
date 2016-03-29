/**
 * @fileOverview Instances landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('InstancesPage', ['LandingPage', 'EucaConsoleUtils', 'smart-table'])
    .controller('InstancesCtrl', function ($scope, $timeout, $http, eucaUnescapeJson, eucaHandleError) {
        $scope.instanceID = '';
        $scope.fileName = '';
        $scope.ipAddresses = [];
        $scope.ipAddressList = {};
        $scope.associateIPModal = $('#associate-ip-to-instance-modal');
        $scope.addressesEndpoint = '';
        $scope.multipleItemsSelected = false;
        $scope.initChosenSelectors = function () {
            $scope.associateIPModal.on('open.fndtn.reveal', function () {
                $('#ip_address').chosen({'width': '80%'});
                $('#ip_address').trigger('chosen:updated');
            });
        };
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.cloudType = options.cloud_type;
            $scope.addressesEndpoint = options.addresses_json_items_endpoint;
            $scope.rolesEndpoint = options.roles_json_items_endpoint;
            $scope.getIPAddresses(); 
            $scope.initChosenSelectors();
            $('#file').on('change', $scope.getPassword);
        };
        $scope.createImageClicked = function (item) {
            if (item.running_create) {
                $scope.instanceID = item.id;
                var modal = $('#create-image-denied-modal');
                modal.foundation('reveal', 'open');
            }
            else {
                window.location = '/instances/' + item.id + '/createimage';
            }
        };
        $scope.revealModal = function (action, instance) {
            var modal = $('#' + action + '-instance-modal'),
                securityGroups = instance.security_groups,
                securityGroupName = 'default';
            if (securityGroups && securityGroups.length) {
                securityGroupName = securityGroups[0].name || instance.security_groups[0].id;
            }
            $scope.instanceID = instance.id;
            $scope.instanceName = instance.name;
            $scope.instancePublicIP = instance.ip_address;
            $scope.rootDevice = instance.root_device;
            $scope.groupName = securityGroupName;
            $scope.securityGroups = securityGroups;
            $scope.keyName = instance.key_name;
            $scope.publicDNS = instance.public_dns_name;
            $scope.platform = instance.platform;
            $scope.ipAddress = instance.ip_address;
            if (action === 'associate-ip-to') {
                $scope.adjustIPAddressOptions(instance);
                // timeout is needed for ipAddressList to be updated
                $timeout(function () {
                    $('#ip_address').trigger('chosen:updated');
                });
            }
            modal.foundation('reveal', 'open');
        };
        $scope.revealMultiSelectModal = function (action, selectedItems) {
            var modal = $('#' + action + '-instance-modal');
            var instanceIDs = [];
            var instanceNames = [];
            var instanceIPs = [];
            if (action === 'disassociate-ip-from') {
                // Disassociate IP action is a special case
                selectedItems.forEach(function (item) {
                    if (item.has_elastic_ip) {
                        instanceIDs.push(item.id);
                        instanceNames.push(item.name || item.id);
                        instanceIPs.push(item.ip_address);
                    }
                });
                $scope.ipAddress = instanceIPs.map(function (ipAddress) {
                    return ipAddress;
                }).join(', ');
            } else {
                selectedItems.forEach(function (item) {
                    instanceIDs.push(item.id);
                    instanceNames.push(item.name || item.id);
                });
            }
            $scope.multipleItemsSelected = instanceIDs.length > 1;
            $scope.instanceID = instanceIDs.join(', ');
            $scope.instanceName = instanceNames.join(', ');
            modal.foundation('reveal', 'open');
        };
        $scope.removeFromView = function(instance, url) {
            url = url.replace("_id_", instance.id);
            var data = "csrf_token=" + $('#csrf_token').val() + "&instance_id=" + instance.id;
            $http({method:'POST', url:url, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.$broadcast('refresh');
                Notify.success("Successfully removed terminated instance");
              }).
              error(function (oData, status) {
                if (status === 403) {
                    $('#timed-out-modal').foundation('reveal', 'open');
                }
                var errorMsg = oData.message || '';
                Notify.failure(errorMsg);
              });
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
                if (evt.target.readyState === FileReader.DONE) {
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
                        if (status === 403) {
                            $('#timed-out-modal').foundation('reveal', 'open');
                        }
                        var errorMsg = oData.message || '';
                        Notify.failure(errorMsg);
                      });
                }
            };
            reader.readAsText(file);
        };
        $scope.revealConsoleOutputModal = function(instance) {
            $(document).trigger('click');
            $scope.instanceName = instance.name;
            var consoleOutputEndpoint = "/instances/" + instance.id + "/consoleoutput/json";
            $scope.consoleOutput = '';
            $http.get(consoleOutputEndpoint).success(function(oData) {
                var results = oData ? oData.results : '';
                if (results) {
                    $scope.consoleOutput = $.base64.decode(results);
                    $('#console-output-modal').foundation('reveal', 'open');
                }
            }).error(function (oData, status) {
                eucaHandleError(oData, status);
            });
        };
        $scope.getCreateLaunchConfigPath = function (item) {
            var securityGroupsList = '';
            angular.forEach(item.security_groups, function (sgroup, index) {
                securityGroupsList += sgroup.id;
                if (index < item.security_groups.length - 1) {
                    securityGroupsList += ",";
                }
            });
            var launchConfigPath =  "/launchconfigs/new?image_id=" + item.image_id +
                "&amp;instance_type=" + item.instance_type +
                "&amp;keypair=" + item.key_name +
                "&amp;security_group=" + securityGroupsList +
                "&amp;userdata_instanceid=" + item.id +
                "&amp;preset=true";
            return launchConfigPath;
        };
        $scope.getIPAddresses = function () {
            var csrf_token = $('#csrf_token').val();
            var data = "csrf_token=" + csrf_token;
            $http({
                method:'POST', url:$scope.addressesEndpoint, data:data,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.ipAddresses = results;
            }).error(function (oData) {
                eucaHandleError(oData, status);
            });
        };
        $scope.adjustIPAddressOptions = function (instance) {
            $scope.ipAddressList = {};
            if (instance.vpc_name === '') {
                angular.forEach($scope.ipAddresses, function(ip){
                    if (ip.domain === 'standard') {
                        if (ip.instance_id === '' || ip.instance_id === null) {
                            $scope.ipAddressList[ip.public_ip] = ip.public_ip;
                        }
                    }
                }); 
            } else {
                angular.forEach($scope.ipAddresses, function(ip){
                    if (ip.domain === 'vpc') {
                        if (ip.instance_id === '' || ip.instance_id === null) {
                            $scope.ipAddressList[ip.public_ip] = ip.public_ip;
                        }
                    }
                }); 
            }
        };
        $scope.$on('itemsLoaded', function($event, items) {
            var theItems = items;
            if ($scope.cloudType === 'euca') {
                $http.get($scope.rolesEndpoint).success(function(oData) {
                    var results = oData ? oData.results : [];
                    for (var k=0; k<theItems.length; k++) {
                        if (results[theItems[k].id] !== undefined) {
                            theItems[k].roles = results[theItems[k].id];
                        }
                    }
                }).error(function (oData, status) {
                    // ignore
                });
            }
        });
    }).filter('hasElasticIP', function() {
        return function (items) {
            return items.filter(function (item) {
                return item.has_elastic_ip;
            });
        };
    })
;
