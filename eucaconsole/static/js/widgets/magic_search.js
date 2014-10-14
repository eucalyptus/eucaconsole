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
            angular.forEach(initialFacets, function(facet, idx) {
                angular.forEach($scope.facetsObj, function(value, idx) {
                    if (value.name == facet) {
                        $scope.currentSearch.push(value);
                        // remove values for this facet
                        var facet_name = value.name.slice(0, value.name.indexOf('='));
                        angular.forEach($scope.facetsObj.slice(), function(facet, idx) {
                            if (facet.name.indexOf(facet_name) == 0) {
                                $scope.facetsObj.splice($scope.facetsObj.indexOf(facet), 1);
                            }
                        });
                    }
                });
            });
            $('#search-text').chosen({search_contains: true, create_option: function(term){
                    var chosen = this;
                    var text_search = 'text='+term;
                    $scope.currentSearch.push({'name':text_search, 'label':text_search});
                    $scope.$apply();
                    $scope.$emit('textSearch', term, $scope.filter_keys);
                },
                create_with_enter: true,
                create_option_text: 'Text Search',
                placeholder_text_single: "Search...",
            });
            $(document).ready(function() {
                $('#search-text').val('').trigger('chosen:updated'); 
            });
            $scope.$watch('searchFacet', function() {
                if ($scope.searchFacet !== '' && $scope.searchFacet !== undefined) {
                    angular.forEach($scope.facetsObj, function(value, idx) {
                        if (value.name == $scope.searchFacet) {
                            $scope.currentSearch.push(value);
                            $scope.emitQuery();
                            return;
                        }
                    });
                }
            });
        };
        $scope.emitQuery = function(removed) {
            var query = '';
            for (var i=0; i<$scope.currentSearch.length; i++) {
                if (i > 0) query = query + "&";
                query = query + $scope.currentSearch[i]['name'];
            }
            console.log("query string = "+query);
            if (removed !== undefined && removed.indexOf('text') == 0) {
                $scope.$emit('textSearch', '', $scope.filter_keys);
            }
            else {
                $scope.$emit('searchUpdated', query);
            }
        };
        $scope.removeFacet = function($index, $event) {
            var removed = $scope.currentSearch[$index].name;
            $scope.currentSearch.splice($index, 1);
            $scope.emitQuery(removed);
            // TODO: now, re-enable the facet
        };
    })
;
