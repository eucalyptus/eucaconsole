/**
 * @fileOverview S3 Metadata Editor JS
 * @requires AngularJS
 *
 */
angular.module('S3MetadataEditor', ['ngSanitize'])
    .controller('S3MetadataEditorCtrl', function ($scope, $sanitize) {
        $scope.metadataEditor = $('#s3-metadata-editor');
        $scope.metadataTextarea = $scope.metadataEditor.find('textarea#metadata');
        $scope.metadataArray = [];
        $scope.newMetadataKey = '';
        $scope.newMetadataValue = '';
        $scope.isMetadataNotComplete = true;
        $scope.syncMetadata = function () {
            var metadataObj = {};
            $scope.metadataArray.forEach(function(metadata) {
                metadataObj[metadata.name] = metadata.value;
            });
            $scope.metadataTextarea.val(JSON.stringify(metadataObj));
        };
        $scope.initMetadata = function(metadataJson) {
            // Parse metadata JSON and convert to a list of metadata.
            metadataJson = metadataJson.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
            var metadataObj = JSON.parse(metadataJson);
            Object.keys(metadataObj).forEach(function(key) {
                $scope.metadataArray.push({
                    'name': key,
                    'value': metadataObj[key]
                });
            });
            $scope.syncMetadata();
            $scope.setWatch();
        };
        $scope.getSafeTitle = function (metadata) {
            return $sanitize(metadata.name + ' = ' + metadata.value);
        };
        $scope.removeMetadata = function (index, $event) {
            $event.preventDefault();
            $scope.metadataArray.splice(index, 1);
            $scope.syncMetadata();
            $scope.$emit('s3metadataUpdate');
        };
        $scope.addMetadata = function ($event) {
            $event.preventDefault();
            var metadataEntry = $($event.currentTarget).closest('.metadataentry'),
                metadataKeyField = metadataEntry.find('[name=metadata_key]'),
                metadataValueField = metadataEntry.find('[name=metadata_value]'),
                metadataArrayLength = $scope.metadataArray.length,
                existingMetadataFound = false,
                form = $($event.currentTarget).closest('form');
            if (metadataKeyField.val() && metadataValueField.val()) {
                // Avoid adding a new metadata if the name duplicates an existing one.
                for (var i=0; i < metadataArrayLength; i++) {
                    if ($scope.metadataArray[i].name === metadataKeyField.val()) {
                        existingMetadataFound = true;
                        break;
                    }
                }
                if (existingMetadataFound) {
                    metadataKeyField.focus();
                } else {
                    $scope.metadataArray.push({
                        'name': metadataKeyField.val(),
                        'value': metadataValueField.val(),
                        'fresh': 'new'
                    });
                    $scope.syncMetadata();
                    metadataKeyField.val('').focus();
                    metadataValueField.val('');
                    $scope.$emit('s3metadataUpdate');
                    $scope.newMetadataKey = '';
                    $scope.newMetadataValue = '';
                }
            } else {
                metadataKeyField.val() ? metadataValueField.focus() : metadataKeyField.focus();
            }
        };
        $scope.checkRequiredInput = function () {
            $scope.isMetadataNotComplete = !!($scope.newMetadataKey === '' || $scope.newMetadataValue === '');
        };
        $scope.setWatch = function () {
            $scope.$watch('newMetadataKey', function () {
                $scope.checkRequiredInput();
            });
            $scope.$watch('newMetadataValue', function () {
                $scope.checkRequiredInput();
            });
        };
    })
;
