/**
 * @fileOverview Image Picker JS
 * @requires AngularJS
 *
 */
angular.module('ImagePicker', [])
    .controller('ImagePickerCtrl', function ($rootScope, $scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.batchSize = 100;  // Show 100 items max w/o "show more" enabler
        $scope.ownerAlias = '';
        $scope.jsonEndpointPrefix = '';
        $scope.jsonEndpoint = '';
        $scope.itemsLoading = false;
        $scope.cloudType = 'euca';
        $scope.filtersForm = $('#filters');
        $scope.imagePicker = $('#image-picker');
        $rootScope.imageID = '';
        $scope.urlParams = $.url().param();
        $scope.selectedImageParam = $scope.urlParams['image_id'] || '';
        // Properties for search input filter
        $scope.filterProps = [
            'architecture', 'description', 'id', 'name', 'tagged_name', 'platform_name', 'root_devite_type'
        ];
        $scope.initImagePicker = function (jsonEndpointPrefix, cloudType) {
            $scope.jsonEndpointPrefix = jsonEndpointPrefix;
            $scope.jsonEndpoint = jsonEndpointPrefix + "?state=available";
            $scope.cloudType = cloudType;
            $scope.initChosenSelectors();
            $scope.initFilters();
            $scope.getItems();
        };
        $scope.initChosenSelectors = function () {
            $scope.filtersForm.find('select').chosen({
                'width': '100%',
                'search_contains': true,
                'placeholder_text_single': ' ',
                'placeholder_text_multiple': ' '
            });
        };
        $scope.initFilters = function () {
            var form = $scope.filtersForm,
                submitBtn = form.find('button[type=submit]'),
                clearLink = form.find('.clear-link');
            submitBtn.on('click', function (evt) {
                evt.preventDefault();
                var architecture, ownerAlias, platform, rootDeviceType, tags;
                var params = {};
                platform = form.find('#platform').val();
                if ($scope.cloudType === 'euca') {
                    params['platform'] = platform;
                } else if ($scope.cloudType === 'aws' && platform) {
                    params['platform'] = platform;
                }
                ownerAlias = form.find('#owner_alias').val();
                rootDeviceType = form.find('#root_device_type').val();
                architecture = form.find('#architecture').val();
                tags = form.find('#tags').val();
                if (ownerAlias) { params['owner_alias'] = ownerAlias; }
                if (rootDeviceType) { params['root_device_type'] = rootDeviceType; }
                if (architecture) { params['architecture'] = architecture; }
                if (tags) { params['tags'] = tags; }
                $scope.jsonEndpoint = decodeURIComponent($scope.jsonEndpointPrefix + "&" + $.param(params, true));
                $scope.getItems();
            });
            clearLink.on('click', function (evt) {
                evt.preventDefault();
                form.find("select").val('').trigger("chosen:updated");
                $scope.jsonEndpoint = $scope.jsonEndpointPrefix;
                $scope.getItems();
            });
        };
        $scope.getItems = function () {
            $scope.searchFilter = '';
            $scope.itemsLoading = true;
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
            });
        };
        $scope.searchImages = function () {
            $scope.items = $scope.unfilteredItems;  // reset prior to applying filter
            var filterText = ($scope.searchFilter || '').toLowerCase();
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.items.filter(function(item) {
                for (var i=0; i < $scope.filterProps.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = $scope.filterProps[i];
                    var itemProp = item.hasOwnProperty(propName) && item[propName];
                    if (itemProp && typeof itemProp === "string" && itemProp.toLowerCase().indexOf(filterText) !== -1) {
                        return item;
                    }
                }
            });
            $scope.items = filterText ? filteredItems : $scope.unfilteredItems;
        };
        $scope.imageSelected = function (item) {
            $scope.selectedImageParam = item.id;
            $scope.$emit('imageSelected', item);
        };
    })
;
