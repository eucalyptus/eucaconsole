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
        $scope.actionsList = [];
        $scope.initController = function (options) {
            $scope.policyJsonEndpoint = options['policyJsonEndpoint'];
            $scope.cloudType = options['cloudType'];
            $scope.actionsList = options['actionsList'];
            $scope.initSelectedTab();
            $scope.initCodeMirror();
            $scope.handlePolicyFileUpload();
            if ($scope.cloudType === 'euca') {
                $scope.initChosenSelectors();
                $scope.addResourceTypeListener();
            }
        };
        $scope.initSelectedTab = function () {
            var lastSelectedTab = localStorage.getItem($scope.lastSelectedTabKey) || 'select-template-tab';
            $('.tabs').find('a').on('click', function (evt) {
                var tabLinkId = $(evt.target).closest('a').attr('id');
                localStorage.setItem($scope.lastSelectedTabKey, tabLinkId);
            });
            $('#' + lastSelectedTab).click();
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
                resourceWrapper.find('input').addClass('hide');
                resourceWrapper.find(resourceSelector).next('.chosen-container').removeClass('hide');
                resourceWrapper.find(resourceSelector).removeClass('hide');
            });
        };
        $scope.initChosenSelectors = function () {
            $timeout(function () {
                $scope.policyGenerator.find('select.chosen').chosen({'width': '44%', 'search_contains': true});
                $scope.limitResourceChoices();
            }, 100);
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
            $scope.policyStatements = [];
            // Add namespace (allow/deny all) statements
            $scope.policyGenerator.find('tr.namespace').each(function (idx, elem) {
                var selectedMark = $(elem).find('.tick.selected');
                if (selectedMark.length > 0) {
                    $scope.policyStatements.push({
                        "Action": selectedMark.attr('data-action'),
                        "Resource": selectedMark.attr('data-resource'),
                        "Effect": selectedMark.attr('data-effect')
                    });
                }
            });
            // Add allow/deny statements for each action
            $scope.actionsList.forEach(function (action) {
                var actionRow = $scope.policyGenerator.find('.action.' + action),
                    selectedMark = actionRow.find('.tick.selected'),
                    addedResources = $scope[action + 'Resources'],
                    addedConditions = $scope[action + 'Conditions'],
                    statement, resource;
                resource = addedResources.length > 0 ? addedResources : selectedMark.attr('data-resource');
                statement = {
                    "Action": selectedMark.attr('data-action'),
                    "Resource": resource,
                    "Effect": selectedMark.attr('data-effect')
                };
                if (Object.keys(addedConditions).length > 0) {
                    statement["Conditions"] = addedConditions;
                }
                if (selectedMark.length > 0) {
                    $scope.policyStatements.push(statement);
                }
            });
            var generatorPolicy = { "Version": $scope.policyAPIVersion, "Statement": $scope.policyStatements };
            var formattedResults = JSON.stringify(generatorPolicy, null, 2);
            $scope.policyText = formattedResults;
            $scope.codeEditor.setValue(formattedResults);
        };
        $scope.addResource = function (action, $event) {
            var resourceBtn = $($event.target),
                actionRow = resourceBtn.closest('tr'),
                selectedTick = actionRow.find('i.selected'),
                allowDenyCount = selectedTick.length,
                actionResources = $scope[action + 'Resources'],
                visibleResource = null,
                resourceVal = null;
            $event.preventDefault();
            visibleResource = actionRow.find('.chosen-container:visible').prev('.resource');
            if (visibleResource.length) {
                resourceVal = visibleResource.val();
            } else {
                visibleResource = actionRow.find('.resource:visible');
                if (visibleResource.hasClass('ip_address')) {
                    // IP Address requires prefix to be set here since it's an input field
                    resourceVal = 'arn:aws:ec2:::address/' + visibleResource.val();
                } else {
                    resourceVal = visibleResource.val();
                }
            }
            resourceVal = resourceVal || '*';
            if (actionResources.indexOf(resourceVal === -1)) {
                actionResources.push(resourceVal);
            }
            if (allowDenyCount === 0) {
                actionRow.find('i.fi-check').addClass('selected');
            }
            actionRow.find('input').focus();
            $scope.updatePolicy();
        };
        $scope.removeResource = function (action, index, $event) {
            $event.preventDefault();
            $scope[action + 'Resources'].splice(index, 1);
            $scope.updatePolicy();
        };
        $scope.addCondition = function (action, $event) {
            var conditionBtn = $($event.target),
                actionRow = conditionBtn.closest('tr'),
                selectedTick = actionRow.find('i.selected'),
                allowDenyCount = selectedTick.length,
                actionConditions = $scope[action + 'Conditions'],
                conditionKey, conditionOperator, conditionValue;
            $event.preventDefault();
            conditionKey = actionRow.find('.condition-keys').val();
            conditionOperator = actionRow.find('.condition-operators').val();
            conditionValue = actionRow.find('.condition-value').val();
            if (!actionConditions[conditionOperator]) {
                actionConditions[conditionOperator] = {};
            }
            actionConditions[conditionOperator][conditionKey] = conditionValue;
            if (allowDenyCount === 0) {
                actionRow.find('i.fi-check').addClass('selected');
            }
            $scope.updateParsedConditions(action, actionConditions);
            $scope.updatePolicy();
        };
        $scope.removeCondition = function (action, operator, key, $event) {
            $event.preventDefault();
            var actionConditions = $scope[action + 'Conditions'];
            if (actionConditions[operator] && actionConditions[operator][key]) {
                delete actionConditions[operator][key];
            }
            if (Object.keys(actionConditions[operator]).length === 0) {
                delete actionConditions[operator];  // Prevent empty operators in conditions
            }
            $scope.updateParsedConditions(action, actionConditions);
            $scope.updatePolicy();
        };
        $scope.updateParsedConditions = function (action, conditionsObj) {
            // Flatten conditions object into an array of conditions with unique key/operator values
            $scope[action + 'ParsedConditions'] = [];
            Object.keys(conditionsObj).forEach(function (operator) {
                Object.keys(conditionsObj[operator]).forEach(function (conditionKey) {
                    $scope[action + 'ParsedConditions'].push({
                        'operator': operator,
                        'key': conditionKey,
                        'value': conditionsObj[operator][conditionKey]
                    });
                });
            });
        };
        // Handle Allow/Deny selection for a given action
        $scope.selectAction = function ($event) {
            var tgt = $($event.target),
                actionRow = tgt.closest('tr');
            $event.preventDefault();
            tgt.toggleClass('selected');
            if (tgt.hasClass('fi-check')) {
                actionRow.find('.fi-x').removeClass('selected');
            } else {
                actionRow.find('.fi-check').removeClass('selected');
            }
            $scope.updatePolicy();
        };
        // Handle Allow/Deny selection for a given namespace (e.g. Allow all EC2 actions)
        $scope.selectAll = function ($event) {
            $event.preventDefault();
            var tgt = $($event.target),
                actionRow = tgt.closest('tr');
            tgt.toggleClass('selected');
            if (tgt.hasClass('fi-check')) {
                actionRow.find('.fi-x').removeClass('selected');
            } else {
                actionRow.find('.fi-check').removeClass('selected');
            }
            $scope.updatePolicy();
        };
        $scope.toggleAdvanced = function ($event) {
            $($event.target).closest('tr').find('.advanced').toggleClass('hide');
        };
        $scope.hasConditions = function (obj) {
            return Object.keys(obj).length > 0;
        };
    })
;

