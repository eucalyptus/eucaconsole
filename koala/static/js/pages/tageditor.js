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
                    'value': tagsObj[key]
                });
            });
            $scope.syncTags();
        };
        $scope.updateTag = function (index, $event, tagType) {
            var field = $($event.currentTarget);
            var fieldEntry = field.val().trim();  // Strip leading/trailing whitespace
            field.val(fieldEntry);
            // Validate tag key
            $scope.tagEditor.trigger('validate');
            if ($scope.tagEditor.find('[data-invalid]').length) {
                return false;
            }
            if (fieldEntry) {
                $scope.tagsArray[index][tagType] = fieldEntry;
                $scope.syncTags();
            }
        };
        $scope.removeTag = function (index) {
            $scope.tagsArray.splice(index, 1);
            $scope.syncTags();
        };
        $scope.addTag = function ($event) {
            var tagEntry = $($event.currentTarget).closest('.tagentry'),
                tagKeyField = tagEntry.find('.key'),
                tagValueField = tagEntry.find('.value'),
                tagsArrayLength = $scope.tagsArray.length,
                existingTagFound = false;
            if (tagKeyField.val() && tagValueField.val()) {
                // Avoid adding a new tag if the name duplicates an existing one.
                for (var i=0; i < tagsArrayLength; i++) {
                    if ($scope.tagsArray[i].name === tagKeyField.val()) {
                        existingTagFound = true;
                        break;
                    }
                }
                if (existingTagFound) {
                    tagKeyField.focus();
                } else {
                    $scope.tagsArray.push({
                        'name': tagKeyField.val(),
                        'value': tagValueField.val(),
                        'fresh': 'new'
                    });
                    $scope.syncTags();
                    tagKeyField.val('').focus();
                    tagValueField.val('');
                }
            } else {
                tagKeyField.val() ? tagValueField.focus() : tagKeyField.focus();
            }
        };
    })
;
