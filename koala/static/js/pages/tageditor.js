/**
 * @fileOverview Tag Editor JS
 * @requires AngularJS
 *
 */
angular.module('TagEditor', [])
    .controller('TagEditorCtrl', function ($scope, $http) {
        $scope.syncTagsTextarea = function() {
            var tagEditor = $('#tag-editor'),
                tagInputs = tagEditor.find('.taginput'),
                tagsTextarea = tagEditor.find('textarea#tags'),
                tagsObj = {};
            tagInputs.on('keyup', function() {
                var tagEntries = tagEditor.find('.tagentry');
                tagEntries.each(function(idx, elem) {
                    var tagEntry = $(elem),
                        tagKey = tagEntry.find('.key').val();
                    tagsObj[tagKey] = tagEntry.find('.value').val();
                });
                tagsTextarea.val(JSON.stringify(tagsObj));
            });
        };
    })
;
