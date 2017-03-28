/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Key pairs landing page JS
 * @requires AngularJS, jQuery
 *
 */

// Pull in common landing page module
angular.module('QueuesPage', ['LandingPage', 'smart-table'])
    .controller('QueuesCtrl', function ($scope) {
        $scope.queueName= '';
        $scope.multipleItemsSelected = false;
        $scope.revealModal = function (action, queueName) {
            queueName = queueName || '';
            var modal = $('#' + action + '-queue-modal');
            $scope.queueName = queueName;
            modal.foundation('reveal', 'open');
        };
        $scope.revealMultiSelectModal = function (action, selectedItems) {
            var modal = $('#' + action + '-queue-modal'),
                itemNames = [];
            selectedItems.forEach(function (item) {
                itemNames.push(item.name || item.id);
            });
            $scope.multipleItemsSelected = itemNames.length > 1;
            $scope.queueName = itemNames.join(', ');
            modal.foundation('reveal', 'open');
        };
    });

