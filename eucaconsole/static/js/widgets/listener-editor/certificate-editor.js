angular.module('ELBCertificateEditorModule', ['ModalModule'])
.directive('certificateEditor', function () {
    return {
        restrict: 'E',
        require: {
            stepData: '?^^stepData'
        },
        scope: {
            certificate: '=ngModel',
            certsAvailable: '='
        },
        templateUrl: '/_template/elbs/listener-editor/certificate-editor',
        link: function (scope, element, attrs, ctrls) {
            var stepData = ctrls.stepData || {};

            scope.certificates = stepData.certificates;
            scope.policies = stepData.policies;
        },
        controller: ['$scope', 'CertificateService', 'ModalService', function ($scope, CertificateService, ModalService) {
            this.activeTab = 'SSL';

            this.showTab = function (tab) {
                this.activeTab = tab;
            };

            this.submitSsl = function () {
                CertificateService.createCertificate({
                    name: this.name,
                    privateKey: this.privateKey,
                    publicKey: this.publicKey,
                    certificateChain: this.certificateChain
                }).then(function success () {
                    ModalService.closeModal('certificateModal');
                }, function error () {
                });
            };

            this.submitBackend = function () {
            };
        }],
        controllerAs: 'ctrl'
    };
})
.factory('CertificateService', ['$http', function ($http) {
    var svc = {
        getCertificates: function () {
            return $http({
                method: 'GET',
                url: '/certificate'
            }).then(function (result) {
                return result.data && result.data.message;
            });
        },

        createCertificate: function (cert) {
            return $http({
                method: 'POST',
                url: '/certificate',
                data: cert
            })//.then(function () {
            //});
            ;
        }
    };

    return svc;
}]);
