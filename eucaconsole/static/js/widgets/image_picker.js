/**
 * @fileOverview Image Picker JS
 * @requires AngularJS
 *
 */
angular.module('ImagePicker', ['EucaConsoleUtils', 'MagicSearch'])
    .controller('ImagePickerCtrl', function ($rootScope, $scope, $http, $timeout, eucaUnescapeJson) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        var unfilteredItems = [];
        var facetItems = [];
        $scope.items = [];
        $scope.itemsLoading = false;
        $scope.batchSize = 100;  // Show 100 items max w/o "show more" enabler
        $scope.ownerAlias = '';
        $scope.jsonEndpointPrefix = '';
        $scope.jsonEndpoint = '';
        $scope.cloudType = 'euca';
        $scope.filtersForm = $('#filters');
        $scope.imagePicker = $('#image-picker');
        $rootScope.imageID = '';
        $scope.urlParams = $.url().param();
        $scope.selectedImageParam = $scope.urlParams.image_id || '';
        // Properties for search input filter
        $scope.filterProps = [
            'architecture', 'description', 'id', 'name', 'tagged_name', 'platform_name', 'root_device_type'
        ];
        $scope.serverFilter = false;
        $scope.initImagePicker = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.jsonEndpointPrefix = options.images_json_endpoint + "?state=available";
            $scope.jsonEndpoint = $scope.jsonEndpointPrefix;
            $scope.cloudType = options.cloud_type;
            $scope.initChosenSelectors();
            $scope.initFilters();
            $scope.getItems();
            if (options.cloud_type !== undefined && options.cloud_type === "aws") {
                $scope.serverFilter = true;
            }
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
                if ($scope.cloudType === 'euca' && platform) {
                    params.platform = platform;
                } else if ($scope.cloudType === 'aws' && platform) {
                    params.platform = platform;
                }
                ownerAlias = form.find('#owner_alias').val();
                rootDeviceType = form.find('#root_device_type').val();
                architecture = form.find('#architecture').val();
                tags = form.find('#tags').val();
                if (ownerAlias) { params.owner_alias = ownerAlias; }
                if (rootDeviceType) { params.root_device_type = rootDeviceType; }
                if (architecture) { params.architecture = architecture; }
                if (tags) { params.tags = tags; }
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
            var csrf_token = $('#csrf_token').val();
            var data = "csrf_token="+csrf_token;
            $http({method:'POST', url:$scope.jsonEndpoint, data:data,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
              success(function(oData) {
                var results = oData ? oData.results : [];
                $scope.itemsLoading = false;
                unfilteredItems = results;
                if ($scope.serverFilter === false) {
                    $scope.facetFilterItems();
                }
                else {
                    facetItems = unfilteredItems;
                    $scope.facetFilterItems();
                }
            });
        };
        var matchByFacet = function(facet, val) {
            if (typeof val === 'string') {
                if ($.inArray(val, facet) > -1 ||
                    $.inArray(val.toLowerCase(), facet) > -1) {
                    return true;
                }
            }
            if (typeof val === 'object') {
                // if object, assume it has valid id or name attribute
                if ($.inArray(val.id, facet) > -1 ||
                    $.inArray(val.name, facet) > -1) {
                    return true;
                }
            }
        };
        var filterByFacet = function(item) {
            // handle special case of empty facet value, match all
            if (this.facet.indexOf("") > -1) {
                return true;
            }
            var val = item[this.key];
            if (val === undefined || val === null) {
                return false;
            }
            if (Array.isArray(val)) {
                for (var i=0; i<val.length; i++) {
                    return matchByFacet(this.facet, val[i]);
                }
            }
            else {
                return matchByFacet(this.facet, val);
            }
        };
        /*  Apply facet filtering
         *  to apply text filtering, call searchFilterItems instead
         */
        $scope.facetFilterItems = function() {
            if ($scope.query !== undefined && $scope.query.length !== 0) {
                // prepare facets by grouping
                var tmp = $scope.query.split('&').sort();
                var facets = {};
                angular.forEach(tmp, function(item) {
                    var facet = item.split('=');
                    if (this[facet[0]] === undefined) {
                        this[facet[0]] = [];
                    }
                    this[facet[0]].push(facet[1]);
                }, facets);
                var results = unfilteredItems;
                // filter results
                for (var key in facets) {
                    results = results.filter(filterByFacet, {'facet': facets[key], 'key':key});
                }
                facetItems = results;
            }
            else {
                facetItems = unfilteredItems.slice();
            }
            $scope.searchImages();
        };
        $scope.searchImages = function () {
            var filterText = ($scope.searchFilter || '').toLowerCase();
            if (filterText === '') {
                // If the search filter is empty, skip the filtering
                $scope.items = facetItems;
                return;
            }
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = facetItems.filter(function(item) {
                for (var i=0; i < $scope.filterProps.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = $scope.filterProps[i];
                    var itemProp = item.hasOwnProperty(propName) && item[propName];
                    if (itemProp && typeof itemProp === "string" && 
                        itemProp.toLowerCase().indexOf(filterText) !== -1) {
                        return item;
                    } else if (itemProp && typeof itemProp === "object") {
                        // In case of mutiple values, create a flat string and perform search
                        var flatString = $scope.getItemNamesInFlatString(itemProp);
                        if (flatString.toLowerCase().indexOf(filterText) !== -1) {
                            return item;
                        }
                    }
                }
            });
            $scope.items = filteredItems;
        };
        $scope.imageSelected = function (item) {
            $scope.selectedImageParam = item.id;
            $scope.$emit('imageSelected', item);
        };
        $scope.$on('searchUpdated', function($event, query) {
            // update url
            var url = window.location.href;
            if (url.indexOf("?") > -1) {
                url = url.split("?")[0];
            }
            if (query.length > 0) {
                url = url + "?" + query;
            }
            window.history.pushState(query, "", url);
            if ($scope.serverFilter === true) {
                url = $scope.jsonEndpoint;
                if (url.indexOf("?") > -1) {
                    url = url.split("?")[0];
                }
                if (query.length > 0) {
                    url = url + "?" + query;
                }
                $scope.jsonEndpoint = url;
                $scope.itemsLoading=true;
                $scope.getItems();
            }
            else {
                $scope.query = query;
                $scope.facetFilterItems();
            }
        });
        $scope.$on('textSearch', function($event, text, filter_keys) {
            $scope.searchFilter = text;
            $timeout(function() {
                $scope.searchImages();
            });
        });
    })
;
