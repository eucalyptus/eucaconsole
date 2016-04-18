angular.module('lpModel', [])
.service('lpModelService', function() {
    var sortBy;
    return {
        setSortBy: function(val) {
            sortBy = val;
        },
        getSortBy: function() {
            return sortBy;
        }
    };
});
