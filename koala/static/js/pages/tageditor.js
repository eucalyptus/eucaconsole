/**
 * @fileOverview Tag Editor JS
 * @requires AngularJS
 *
 */
angular.module('TagEditor', [])
    .controller('TagEditorCtrl', function ($scope, $http) {
        $scope.tagEditor = $('#tag-editor');
        $scope.tagInputs = $scope.tagEditor.find('.taginput');
        $scope.tagsTextarea = $scope.tagEditor.find('textarea#tags');
        $scope.tagsObj = {};
        $scope.syncTagsTextarea = function() {
            var tagEntries = $scope.tagEditor.find('.tagentry');
            tagEntries.each(function(idx, elem) {
                var tagEntry = $(elem),
                    tagKey = tagEntry.find('.key').val(),
                    tagValue = tagEntry.find('.value').val();
                if (tagKey && tagValue) {
                    $scope.tagsObj[tagKey] = tagValue;
                }
            });
            $scope.tagsTextarea.val(JSON.stringify($scope.tagsObj));
        };
        $scope.syncTagsTextarea();
        $scope.tagInputs.on('keyup', function() {
            $scope.syncTagsTextarea();
        });
    })
;
