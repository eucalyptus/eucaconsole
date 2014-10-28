/**
 * @fileOverview Magic Search JS
 * @requires AngularJS
 *
 */
angular.module('MagicSearch', [])
    .controller('MagicSearchCtrl', function ($scope, $timeout) {
        $scope.currentSearch = [];
        $scope.searchFacet = '';
        $scope.initSearch = function(facetsJson, filter_keys) {
            $scope.filter_keys = filter_keys;
            // Parse facets JSON and convert to a list of facets.
            facetsJson = facetsJson.replace(/__apos__/g, "\'").replace(/__dquote__/g, '\\"').replace(/__bslash__/g, "\\");
            $scope.facetsObj = JSON.parse(facetsJson);
            // set facets selected and remove them from facetsObj
            var initialFacets = window.location.search
            if (initialFacets.indexOf('?') == 0) {
                initialFacets = initialFacets.slice(1);
            }
            initialFacets = initialFacets.split('&');
            if (initialFacets.length > 1 || initialFacets[0].length > 0) {
                $('#search-input').removeAttr('placeholder');
            }
            angular.forEach(initialFacets, function(facet, idx) {
                var facetParts = facet.split('=');
                angular.forEach($scope.facetsObj, function(value, idx) {
                    if (value.name == facetParts[0]) {
                        if (value.name == 'tags') {
                            $scope.currentSearch.push({'name':facet, 'label':[value.label, facetParts[1]]});
                            // allow tags to stay since we can have multiples
                        }
                        else {
                            angular.forEach(value.options, function(option, idx) {
                                if (option.key == facetParts[1]) {
                                    $scope.currentSearch.push({'name':facet, 'label':[value.label, option.label]});
                                    $scope.deleteFacetSelection(facetParts);
                                }
                            });
                        }
                    }
                });
            });
        };
        // removes a facet from the menu
        $scope.deleteFacetSelection = function(facet_parts) {
            angular.forEach($scope.facetsObj.slice(), function(facet, idx) {
                if (facet.name == facet_parts[0]) {
                    for (var i=0; i<facet.options.length; i++) {
                        var option = facet.options[i];
                        if (option.key == facet_parts[1]) {
                            $scope.facetsObj[idx].options.splice($scope.facetsObj[idx].options.indexOf(option), 1);
                        }
                    }
                    if (facet.options.length == 0) {
                        $scope.facetsObj.splice($scope.facetsObj.indexOf(facet), 1);
                    }
                }
            });
        };
        $('#search-input').on('keypress', function(event) {
            if (event.which == 13) {
                var search_val = $('#search-input').val();
                // if tag search, treat as regular facet
                if ($scope.facetSelected == 'tags') {
                    var curr = $scope.currentSearch[$scope.currentSearch.length-1];
                    curr.name = curr.name + '=' + search_val;
                    curr.label[1] = search_val;
                    $scope.facetSelected = undefined;
                    $scope.emitQuery();
                }
                // if text search treat as search
                else {
                    for (var i=0; i<$scope.currentSearch.length; i++) {
                        if ($scope.currentSearch[i]['name'].indexOf('text') == 0) {
                            $scope.currentSearch.splice(i, 1);
                        }
                    }
                    $scope.currentSearch.push({'name':'text='+search_val, 'label':['text', search_val]});
                    $scope.$apply();
                    $('#search-input').trigger('click');
                    $('#search-input').val('');
                    $scope.$emit('textSearch', search_val, $scope.filter_keys);
                }
            }
        });
        // when facet clicked, add 1st part of facet and set up options
        $scope.facetClicked = function($index, $event, name) {
            $('#search-input').trigger('click');
            $scope.facetSelected = name;
            $scope.currentSearch.push({'name':name, 'label':[$scope.facetsObj[$index].label, '']});
            if (name != 'tags') {
                $scope.facetOptions = $scope.facetsObj[$index].options;
                $timeout(function() {
                    $('#search-input').trigger('click');
                });
            }
            else {
                $('#search-input').focus();
            }
        };
        // when option clicked, complete facet and send event
        $scope.optionClicked = function($index, $event, name) {
            $('#search-input').trigger('click');
            var curr = $scope.currentSearch[$scope.currentSearch.length-1];
            curr.name = curr.name + '=' + name;
            curr.label[1] = $scope.facetOptions[$index].label;
            $scope.facetSelected = undefined;
            $scope.facetOptions = undefined;
            $scope.emitQuery();
        };
        // send event with new query string
        $scope.emitQuery = function(removed) {
            $('#search-input').removeAttr('placeholder');
            var query = '';
            for (var i=0; i<$scope.currentSearch.length; i++) {
                if ($scope.currentSearch[i]['name'].indexOf('text') != 0) {
                    if (query.length > 0) query = query + "&";
                    query = query + $scope.currentSearch[i]['name'];
                }
            }
            if (removed !== undefined && removed.indexOf('text') == 0) {
                $scope.$emit('textSearch', '', $scope.filter_keys);
            }
            else {
                $scope.$emit('searchUpdated', query);
            }
        };
        // remove facet and either update filter or search
        $scope.removeFacet = function($index, $event) {
            var removed = $scope.currentSearch[$index].name;
            $scope.currentSearch.splice($index, 1);
            if ($scope.facetSelected === undefined) {
                $scope.emitQuery(removed);
            }
            else {
                $scope.facetSelected = undefined;
                $scope.facetOptions = undefined;
                $('#search-input').val('');
            }
            // facet re-enabled by reload
        };
        // clear entire searchbar
        $scope.clearSearch = function() {
            if ($scope.currentSearch.length > 0) {
                $scope.currentSearch = [];
                $('#search-input').val('');
                $scope.$emit('searchUpdated', '');
            }
        };
    })
;
