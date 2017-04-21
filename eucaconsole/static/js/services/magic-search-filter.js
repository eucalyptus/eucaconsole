/**
 * Copyright 2017 Ent. Services Development Corporation LP
 *
 * @fileOverview factory method for functions needed by magic search to filter lists of resources
 * @requires AngularJS
 *
 */
angular.module('MagicSearchFilterModule', [])
.factory('MagicSearchFilterService', ['$http', function ($http) {
    var matchByFacet =  function(facet, val) {
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
                return true;
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
    var getItemNamesInFlatString = function(items) {
            var flatString = '';
            angular.forEach(items, function(x) {
                if (x.hasOwnProperty('name')) {
                    flatString += x.name + ' ';
                }
                if (x.hasOwnProperty('res_name')) {
                    flatString += x.res_name + ' ';
                }
            });
            return flatString;
        };
    return {
        /*  Apply facet filtering
         *  to apply text filtering, call searchFilterItems instead
         */
        facetFilterItems: function(query, unfilteredItems) {
            var url = window.location.href;
            if (url.indexOf("?") > -1) {
                query = url.split("?")[1];
            }
            if (query !== undefined && query.length !== 0) {
                // prepare facets by grouping
                var tmp = query.split('&').sort();
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
                return results;
            }
            else {
                return unfilteredItems.slice();
            }
        },
        /*  Filter items client side based on search criteria.
         */
        searchFilterItems: function(searchFilter, filterKeys, facetItems) {
            var filterText = (searchFilter || '').toLowerCase();
            if (filterText === '') {
                // If the search filter is empty, skip the filtering
                return facetItems;
            }
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = facetItems.filter(function(item) {
                for (var i=0; i < filterKeys.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = filterKeys[i];
                    var itemProp = item.hasOwnProperty(propName) && item[propName];
                    if (itemProp && typeof itemProp === "string" && 
                        itemProp.toLowerCase().indexOf(filterText) !== -1) {
                        return item;
                    } else if (itemProp && typeof itemProp === "object") {
                        // In case of mutiple values, create a flat string and perform search
                        var flatString = getItemNamesInFlatString(itemProp);
                        if (flatString.toLowerCase().indexOf(filterText) !== -1) {
                            return item;
                        }
                    }
                }
            });
            return filteredItems;
        }
    };
}]);

