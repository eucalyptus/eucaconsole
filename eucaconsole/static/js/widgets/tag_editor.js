/**
 * @fileOverview Tag Editor JS
 * @requires AngularJS
 *
 */
angular.module('TagEditor', ['ngSanitize'])
    .filter('ellipsis', function () {
        return function (line, num) {
            if( line.length <= num ){
                return line;
            }
            return line.substring(0, num) + "...";
        };
    })
    .controller('TagEditorCtrl', function ($scope, $sanitize) {
        $scope.tagEditor = $('#tag-editor');
        $scope.tagInputs = $scope.tagEditor.find('.taginput');
        $scope.tagsTextarea = $scope.tagEditor.find('textarea#tags');
        $scope.tagsArray = [];
        $scope.showNameTag = true;
        $scope.visibleTagsCount = 0;
        $scope.syncTags = function () {
            var tagsObj = {};
            $scope.tagsArray.forEach(function(tag) {
                tagsObj[tag.name] = tag.value;
            });
            $scope.tagsTextarea.val(JSON.stringify(tagsObj));
            // Update visible tags count, ignoring "Name" tag when present.
            $scope.updateVisibleTagsCount();
        };
        $scope.updateVisibleTagsCount = function () {
            if ($scope.showNameTag) {
                $scope.visibleTagsCount = $scope.tagsArray.length;
            } else {
                // Adjust count if "Name" tag is in tagsArray
                $scope.visibleTagsCount = $.map($scope.tagsArray, function (item) {
                    if (item.name !== 'Name') { return item; }
                }).length;
            }
        };
        $scope.initTags = function(tagsJson, showNameTag) {
            // Parse tags JSON and convert to a list of tags.
            tagsJson = tagsJson.replace(/__apos__/g, "\'");
            var tagsObj = JSON.parse(tagsJson);
            Object.keys(tagsObj).forEach(function(key) {
                if (!key.match(/^aws:.*/)) {
                    $scope.tagsArray.push({
                        'name': key,
                        'value': tagsObj[key]
                    });
                }
            });
            $scope.showNameTag = showNameTag;
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
        $scope.addTag = function ($event) {
            $event.preventDefault();
            var tagEntry = $($event.currentTarget).closest('.tagentry'),
                tagKeyField = tagEntry.find('.key'),
                tagValueField = tagEntry.find('.value'),
                tagsArrayLength = $scope.tagsArray.length,
                existingTagFound = false,
                form = $($event.currentTarget).closest('form'),
                invalidFields = form.find('[data-invalid]');
            if (tagKeyField.val() && tagValueField.val()) {
                // Trigger validation to avoid tags that start with 'aws:'
                form.trigger('validate');
                // checking for keypair here since the keypair widget will always be invalid
                // till the user selects something on the launch wizard. Assume we don't care
                // about keypair validation errors here, but if there's at least one non-
                // keypair error, we'll honor that.
                if (invalidFields.length && invalidFields[0].name!="keypair") {
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
