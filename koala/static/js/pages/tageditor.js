/**
 * @fileOverview Tag Editor JS
 * @requires AngularJS
 *
 */
angular.module('TagEditor', [])
    .controller('TagEditorCtrl', function ($scope) {
        $scope.tagEditor = $('#tag-editor');
        $scope.tagInputs = $scope.tagEditor.find('.taginput');
        $scope.tagsTextarea = $scope.tagEditor.find('textarea#tags');
        $scope.tagsArray = [];
        $scope.syncTags = function () {
            var tagsObj = {};
            $scope.tagsArray.forEach(function(tag) {
                tagsObj[tag.name] = tag.value;
            });
            $scope.tagsTextarea.val(JSON.stringify(tagsObj));
        };
        $scope.initTags = function(tagsJson) {
            // Parse tags JSON and convert to a list of tags.
            var tagsObj = JSON.parse(tagsJson);
            Object.keys(tagsObj).forEach(function(key) {
                $scope.tagsArray.push({
                    'name': key,
                    'value': tagsObj[key],
                    'inserted': true
                });
            });
            $scope.syncTags();
        };
        $scope.updateTagKey = function (index, $event) {
            var newKey = $($event.currentTarget).val();
            if (newKey) {
                $scope.tagsArray[index]['name'] = newKey;
                $scope.syncTags();
            }
        };
        $scope.updateTagValue = function (index, $event) {
            var newVal = $($event.currentTarget).val();
            if (newVal) {
                $scope.tagsArray[index]['value'] = newVal;
                $scope.syncTags();
            }
        };
        $scope.removeTag = function (index) {
            $scope.tagsArray.splice(index, 1);
            $scope.syncTags();
        };
        $scope.addTag = function ($event) {
            var plus = $($event.currentTarget),
                tagEntry = plus.closest('.tagentry'),
                tagKeyField = tagEntry.find('.key'),
                tagValueField = tagEntry.find('.value');
            if (tagKeyField.val() && tagValueField.val()) {
                $scope.tagsArray.push({
                    'name': tagKeyField.val(),
                    'value': tagValueField.val(),
                    'inserted': true
                });
                tagKeyField.val('').focus();
                tagValueField.val('');
                $scope.syncTags();
            } else {
                tagKeyField.val() ? tagValueField.focus() : tagKeyField.focus();
            }
        };
    })
;
