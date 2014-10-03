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
    .controller('TagEditorCtrl', function ($scope, $sanitize, $timeout) {
        $scope.tagEditor = $('#tag-editor');
        $scope.tagInputs = $scope.tagEditor.find('.taginput');
        $scope.tagsTextarea = $scope.tagEditor.find('textarea#tags');
        $scope.tagsArray = [];
        $scope.newTagKey = '';
        $scope.newTagValue = '';
        $scope.showNameTag = true;
        $scope.isTagNotComplete = true;
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
            tagsJson = tagsJson.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
            var tagsObj = JSON.parse(tagsJson);
            Object.keys(tagsObj).forEach(function(key) {
                if (!key.match(/^aws:.*/) && !key.match(/^euca:.*/)) {
                    $scope.tagsArray.push({
                        'name': key,
                        'value': tagsObj[key]
                    });
                }
            });
            $('#tag-name-input').keydown(function(evt) {
                if (evt.keyCode === 13) {
                    evt.preventDefault();
                }
            });
            $('#tag-value-input').keydown(function(evt) {
                if (evt.keyCode === 13) {
                    evt.preventDefault();
                }
            });
            $scope.showNameTag = showNameTag;
            $scope.syncTags();
            $scope.setWatch();
        };
        $scope.getSafeTitle = function (tag) {
            return $sanitize(tag.name + ' = ' + tag.value);
        };
        $scope.removeTag = function (index, $event) {
            $event.preventDefault();
            $scope.tagsArray.splice(index, 1);
            $scope.syncTags();
            $scope.$emit('tagUpdate');
        };
        $scope.addTag = function ($event) {
            $event.preventDefault();
            $scope.checkRequiredInput();
            if ($scope.isTagNotComplete) {
                return;
            }
            var tagEntry = $($event.currentTarget).closest('.tagentry'),
                tagKeyField = tagEntry.find('.key'),
                tagValueField = tagEntry.find('.value'),
                tagsArrayLength = $scope.tagsArray.length,
                existingTagFound = false,
                form = $($event.currentTarget).closest('form');
            if (tagKeyField.val() && tagValueField.val()) {
                // disallow adding tags starting with aws:. abide handles
                // alerting the user
                if (tagKeyField.val().indexOf("aws:") == 0) {
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
                    $scope.$emit('tagUpdate');
                    $scope.newTagKey = '';
                    $scope.newTagValue = '';
                }
            } else {
                tagKeyField.val() ? tagValueField.focus() : tagKeyField.focus();
            }
        };
        $scope.checkRequiredInput = function () {
            if ($scope.newTagKey === '' || $scope.newTagValue === '') {
                $scope.isTagNotComplete = true;
            } else if ($('#tag-name-input-div').hasClass('error') ||
                $('#tag-value-input-div').hasClass('error')) {
                $scope.isTagNotComplete = true;
            } else {
                $scope.isTagNotComplete = false;
            } 

        }; 
        $scope.setWatch = function () {
            $scope.$watch('newTagKey', function () {
                $scope.checkRequiredInput();
                // timeout is needed to react to Foundation's validation check
                $timeout(function() {
                    // repeat the check on input condition 
                    $scope.checkRequiredInput();
                }, 1000);
            });
            $scope.$watch('newTagValue', function () {
                $scope.checkRequiredInput();
                // timeout is needed to react to Foundation's validation check
                $timeout(function() {
                    // repeat the check on input condition 
                    $scope.checkRequiredInput();
                }, 1000);
            });
        };
    })
;
