/**
 * @fileOverview IAM Policy Wizard JS
 * @requires AngularJS
 *
 */

angular.module('IAMPolicyWizard', [])
    .controller('IAMPolicyWizardCtrl', function ($scope, $http, $timeout) {
        $scope.wizardForm = $('#iam-policy-form');
        $scope.policyGenerator = $('#policy-generator');
        $scope.policyJsonEndpoint = '';
        $scope.policyTextarea = document.getElementById('policy');
        $scope.codeEditor = null;
        $scope.policyStatements = [];
        $scope.addedStatements = [];
        $scope.policyAPIVersion = "2012-10-17";
        $scope.cloudType = 'euca';
        $scope.lastSelectedTabKey = 'policyWizard-selectedTab';
        $scope.initController = function (options) {
            $scope.policyJsonEndpoint = options['policyJsonEndpoint'];
            $scope.cloudType = options['cloudType'];
            $scope.initSelectedTab();
            $scope.initCodeMirror();
            $scope.handlePolicyFileUpload();
            if ($scope.cloudType === 'euca') {
                $scope.initChosenSelectors();
                $scope.limitResourceChoices();
                $scope.addResourceTypeListener();
            }
        };
        $scope.initSelectedTab = function () {
            var lastSelectedTab = localStorage.getItem($scope.lastSelectedTabKey) || 'select-template-tab';
            $('#' + lastSelectedTab).click();
            $('.tabs').find('a').on('click', function (evt) {
                var tabLinkId = $(evt.target).closest('a').attr('id');
                localStorage.setItem($scope.lastSelectedTabKey, tabLinkId);
            });
        };
        $scope.limitResourceChoices = function () {
            // Only display the resource field inputs for the relevant actions
            var resourceValueInputs = $scope.policyGenerator.find('.resource.chosen');
            resourceValueInputs.addClass('hide');
            resourceValueInputs.next('.chosen-container').addClass('hide');
            resourceValueInputs.each(function(idx, item) {
                var elem = $(item),
                    resourceType = elem.closest('.resource-wrapper').find('.resource-type').val();
                if (elem.hasClass(resourceType)) {
                    elem.removeClass('hide');
                    elem.next('.chosen-container').removeClass('hide');
                }
            });
        };
        $scope.addResourceTypeListener = function () {
            // Show/hide resource choices based on resource type selection
            var resourceSelects = $scope.policyGenerator.find('select.resource-type');
            resourceSelects.on('change', function(evt) {
                var resourceSelect = $(evt.target),
                    resourceType = resourceSelect.val(),
                    resourceSelector = '.resource.' + resourceType,
                    resourceWrapper = resourceSelect.closest('.resource-wrapper');
                resourceWrapper.find('.chosen-container').addClass('hide');
                resourceWrapper.find(resourceSelector).next('.chosen-container').removeClass('hide');
            });
        };
        $scope.initChosenSelectors = function () {
            $scope.policyGenerator.find('select.chosen').chosen({'width': '44%', 'search_contains': true});
        };
        $scope.initCodeMirror = function () {
            $scope.codeEditor = CodeMirror.fromTextArea($scope.policyTextarea, {
                mode: "javascript",
                lineWrapping: true,
                styleActiveLine: true,
                lineNumbers: true
            });
        };
        $scope.visitStep = function(step) {
            $('#tabStep' + step).click();
        };
        $scope.setPolicyName = function (policyType) {
            var typeNameMapping = {
                'admin_access': 'AccountAdminAccessPolicy',
                'user_access': 'PowerUserAccessPolicy',
                'monitor_access': 'ReadOnlyUserAccessPolicy',
                'blank': 'CustomAccessPolicy'
            }
            $scope.policyName = typeNameMapping[policyType] || '';
        };
        $scope.handlePolicyFileUpload = function () {
            $('#policy_file').on('change', function(evt) {
                var file = evt.target.files[0],
                    reader = new FileReader();
                reader.onloadend = function(evt) {
                    if (evt.target.readyState == FileReader.DONE) {
                        $scope.policyText = evt.target.result;
                        $scope.codeEditor.setValue(evt.target.result);
                        $scope.codeEditor.focus();
                    }
                };
                reader.readAsText(file);
            });
        };
        $scope.selectPolicy = function(policyType) {
            // Fetch hard-coded canned policies
            var jsonUrl = $scope.policyJsonEndpoint + "?type=" + policyType;
            $http.get(jsonUrl).success(function(oData) {
                var results = oData ? oData['policy'] : '',
                    formattedResults = '';
                if (results) {
                    formattedResults = JSON.stringify(results, null, 2);
                    $scope.policyText = formattedResults;
                    $scope.codeEditor.setValue(formattedResults);
                    $scope.codeEditor.focus();
                }
            });
            // Set policy name
            $scope.setPolicyName(policyType);
        };
        $scope.updatePolicy = function() {
            var generatorPolicy = { "Version": $scope.policyAPIVersion, "Statement": $scope.policyStatements };
            var formattedResults = JSON.stringify(generatorPolicy, null, 2);
            $scope.policyText = formattedResults;
            $scope.codeEditor.setValue(formattedResults);
        };
        $scope.updateStatements = function () {
            // TODO: remove and replace all calls with $scope.updatePolicy;
            $scope.policyStatements = [];
            $scope.policyGenerator.find('.action').find('i.selected').each(function(idx, item) {
                var namespace = item.getAttribute('data-namespace'),
                    action = item.getAttribute('data-action'),
                    effect = item.getAttribute('data-effect'),
                    nsAction = namespace.toLowerCase() + ':' + action,
                    actionRow = $(item).closest('tr'),
                    visibleResource = null,
                    resource = null;
                visibleResource = actionRow.find('.chosen-container:visible').prev('.resource');
                if (!visibleResource.length) {
                    visibleResource = actionRow.find('.resource:visible');
                }
                resource = visibleResource.val() || '*';
                $scope.policyStatements.push({
                    "Action": [nsAction],
                    "Resource": resource,
                    "Effect": effect
                });
            });
            $scope.updatePolicy();
        };
        $scope.addResource = function ($event) {
            var resourceBtn = $($event.target),
                actionRow = resourceBtn.closest('tr');
            var allowDenyCount = actionRow.find('i.selected').length;
            if (!allowDenyCount) {
                alert('Select "Allow" or "Deny" to add the statement to the policy');
            } else {
                // TODO: replace with updatePolicy()
                $scope.updateStatements();
            }
        };
        $scope.handleSelection = function ($event) {
            var tgt = $($event.target);
            tgt.toggleClass('selected');
            if (tgt.hasClass('fi-check')) {
                tgt.closest('tr').find('.fi-x').removeClass('selected');
            } else {
                tgt.closest('tr').find('.fi-check').removeClass('selected');
            }
            $timeout(function () {
                // TODO: replace with updatePolicy()
                $scope.updateStatements();
            }, 50);
        };
        $scope.selectAll = function (effect, namespace, $event) {
            // effect is 'Allow' or 'Deny'
            $event.preventDefault();
            $scope.resetNamespacePolicyStatements(namespace);
            var tgt = $($event.target),
                action = namespace + ':*',
                resource = '*',
                nsStatement = {};
            tgt.toggleClass('selected');
            if (tgt.hasClass('fi-check')) {
                tgt.closest('tr').find('.fi-x').removeClass('selected');
            } else {
                tgt.closest('tr').find('.fi-check').removeClass('selected');
            }
            nsStatement = {
                "Action": action,
                "Resource": resource,
                "Effect": effect
            };
            if (tgt.hasClass('selected')) {
                $scope.policyStatements.push(nsStatement);
            }
            $timeout(function () {
                $scope.updatePolicy();
            }, 100)
        };
        $scope.resetNamespacePolicyStatements = function (namespace) {
            $scope.policyStatements.forEach(function (item, idx) {
                if (item['Action'] === namespace + ':*') {
                    $scope.policyStatements.splice(idx, 1);
                }
            });
            console.log($scope.policyStatements)
        }
        $scope.toggleAdvanced = function ($event) {
            $($event.target).closest('tr').find('.advanced').toggleClass('hide');
        };
    })
;

