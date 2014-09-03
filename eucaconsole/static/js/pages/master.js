var generateKeys = function(username) {
    var csrf_token = $('input[name="csrf_token"]').val();
    var data = "csrf_token="+csrf_token;
    var $http = angular.element('div[ng-app]').injector().get('$http');
    $http({method:'POST', url: '/users/'+username+'/genkeys',
           data:data, headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
      success(function(oData) {
        var results = oData ? oData.results : [];
        $('#create-keys-modal').foundation('reveal', 'close');
        Notify.success(oData.message);
        $.generateFile({
            csrf_token: csrf_token,
            filename: 'not-used', // let the server set this
            content: 'none',
            script: '/_getfile',
        });
    }).error(function (oData, status) {
        var errorMsg = oData['message'] || '';
        if (errorMsg && status === 403) {
            $('#timed-out-modal').foundation('reveal', 'open');
        }
        else {
            $('#denied-keys-modal').foundation('reveal', 'open');
        }
    });
    return false;
  };
