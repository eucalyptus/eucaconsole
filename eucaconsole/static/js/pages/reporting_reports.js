angular.module('ReportingPage')
.controller('ReportsController', ['$scope', '$routeParams', 'ReportingService', 'eucaHandleError', function ($scope, $routeParams, ReportingService, eucaHandleError) {
    var vm = this;
    vm.monthChoices = ['January 2017', 'December 2016', 'November 2016'];
    vm.monthlyUsage = [{details:'ec2 instances', total:'4'}, {details:'volumes', total:'5'}];
    vm.values = {
        monthSelection: vm.monthChoices[0],
    };
    vm.showEC2InstanceUsageReport = function() {
    };
    vm.showUsageReportsByService = function() {
    };
    vm.loadMonthlyData = function() {
        // use reports service to load montly report data
        ReportingService.getMonthlyUsage(2017, 1).then(
        function success(result) {
                var data = result.results;
                //vm.monthlyUsage = parseCSV(data);
                vm.monthlyUsage = CSVToArray(data);
            },
            function error(errData) {
                eucaHandleError(errData.data.message, errData.status);
            });
    };
    vm.loadMonthlyData();
    vm.downloadCSV = function() {
        // use reports service to get montly data in csv format
        // use generateFile in success method to present file for user to download
        // see user_view.js for an example
    };
    var parseCSV = function(csv) {
        var ret = csv.split('\n');//.slice(1);
        ret.forEach(function(val, idx, arr) {
            arr[idx] = val.split(',');
            arr[idx].forEach(function(val, idx, arr) {
                arr[idx] = val.replace(/^"(.+(?="$))"$/, '$1');
            });
        });
        return ret;
    };
    // Source: https://gist.github.com/bennadel/9753411#file-code-1-htm
    var CSVToArray = function( strData, strDelimiter ){
        // Check to see if the delimiter is defined. If not,
        // then default to comma.
        strDelimiter = (strDelimiter || ",");
        // Create a regular expression to parse the CSV values.
        var objPattern = new RegExp(
            (
                // Delimiters.
                "(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +
                // Quoted fields.
                "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +
                // Standard fields.
                "([^\"\\" + strDelimiter + "\\r\\n]*))"
            ),
            "gi"
            );
        // Create an array to hold our data. Give the array
        // a default empty first row.
        var arrData = [[]];
        // Create an array to hold our individual pattern
        // matching groups.
        var arrMatches = null;
        // Keep looping over the regular expression matches
        // until we can no longer find a match.
        while (arrMatches = objPattern.exec( strData )){
            // Get the delimiter that was found.
            var strMatchedDelimiter = arrMatches[ 1 ];
            // Check to see if the given delimiter has a length
            // (is not the start of string) and if it matches
            // field delimiter. If id does not, then we know
            // that this delimiter is a row delimiter.
            if (
                strMatchedDelimiter.length &&
                (strMatchedDelimiter != strDelimiter)
                ){
                // Since we have reached a new row of data,
                // add an empty row to our data array.
                arrData.push( [] );
            }
            // Now that we have our delimiter out of the way,
            // let's check to see which kind of value we
            // captured (quoted or unquoted).
            if (arrMatches[ 2 ]){
                // We found a quoted value. When we capture
                // this value, unescape any double quotes.
                var strMatchedValue = arrMatches[ 2 ].replace(
                    new RegExp( "\"\"", "g" ),
                    "\""
                    );
            } else {
                // We found a non-quoted value.
                var strMatchedValue = arrMatches[ 3 ];
            }
            // Now that we have our value string, let's add
            // it to the data array.
            arrData[ arrData.length - 1 ].push( strMatchedValue );
        }
        // Return the parsed data.
        return( arrData );
    };
}]);
