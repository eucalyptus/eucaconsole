/**
 * @fileOverview Images landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('ImagesPage', ['LandingPage'])
    .controller('ImagesCtrl', function ($scope) {
        $scope.imageID = '';
        $scope.revealModal = function (action, image) {
            var modal = $('#' + action + '-image-modal');
            $scope.imageID = image['id'];
            modal.foundation('reveal', 'open');
            var form = $('#deregister-form');
            var formAction = form.attr('action').replace("_id_", image['id']);
            form.attr('action', formAction);
        };
    })
;

