/**
 * @fileOverview Scaling Group Tag Editor JS
 * @requires AngularJS
 *
 */
angular.module('AutoScaleTagEditor', ['ngSanitize'])
    .filter('ellipsis', function () {
        return function (line, num) {
            if (line.length <= num) {
                return line;
            }
            return line.substring(0, num) + "...";
        };
    })
    .controller('AutoScaleTagEditorCtrl', function ($scope, $sanitize) {
        $scope.tagEditor = $('#tag-editor');
        $scope.tagInputs = $scope.tagEditor.find('.taginput');
        $scope.tagsTextarea = $scope.tagEditor.find('textarea#tags');
        $scope.tagsArray = [];
        $scope.syncTags = function () {
            $scope.tagsTextarea.val(JSON.stringify($scope.tagsArray));
        };
        $scope.initTags = function(tagsJson) {
            // Parse tags JSON and convert to a list of tags.
            tagsJson = tagsJson.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__blash__/g, "\\");
            var tagsArray = JSON.parse(tagsJson);
            tagsArray.forEach(function(tag) {
                if (!tag['name'].match(/^aws:.*/)) {
                    $scope.tagsArray.push({
                        'name': tag['name'],
                        'value': tag['value'],
                        'propagate_at_launch': tag['propagate_at_launch']
                    });
                }
            });
            $scope.syncTags();
        };
        $scope.getSafeTitle = function (tag) {
            return $sanitize(tag.name + ' = ' + tag.value);
        };
        $scope.removeTag = function (index, $event) {
            $event.preventDefault();
            $scope.tagsArray.splice(index, 1);
            $scope.syncTags();
        };
        $scope.togglePropagateCheckbox = function () {
            var checkbox = $('#propagate-checkbox');
            checkbox.prop('checked', !checkbox.prop('checked'));
        };
        $scope.addTag = function ($event) {
            $event.preventDefault();
            var tagEntry = $($event.currentTarget).closest('.tagentry'),
                tagKeyField = tagEntry.find('.key'),
                tagValueField = tagEntry.find('.value'),
                tagPropagateField = tagEntry.find('.propagate'),
                tagsArrayLength = $scope.tagsArray.length,
                existingTagFound = false,
                form = $($event.currentTarget).closest('form'),
                invalidFields = form.find('[data-invalid]');
            if (tagKeyField.val() && tagValueField.val()) {
                // Trigger validation to avoid tags that start with 'aws:'
                form.trigger('validate');
                if (invalidFields.length) {
                    invalidFields.focus();
                    return false;
                }
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
                        'propagate_at_launch': tagPropagateField.is(':checked'),
                        'fresh': 'new'
                    });
                    $scope.syncTags();
                    // Reset input fields after adding tag
                    tagKeyField.val('').focus();
                    tagValueField.val('');
                    tagPropagateField.prop('checked', false);
                }
            } else {
                tagKeyField.val() ? tagValueField.focus() : tagKeyField.focus();
            }
        };
    })
;
