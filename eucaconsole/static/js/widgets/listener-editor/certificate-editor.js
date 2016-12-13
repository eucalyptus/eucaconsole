angular.module('ELBCertificateEditorModule', ['ModalModule', 'ELBWizard'])
.directive('certificateEditor', function () {
    return {
        restrict: 'E',
        scope: {
            certificate: '=ngModel'
        },
        templateUrl: '/_template/elbs/listener-editor/certificate-editor',
        controller: ['$scope', 'CertificateService', 'ModalService', 'ELBWizardService', function ($scope, CertificateService, ModalService, ELBWizardService) {
            this.activeTab = 'SSL';
            this.certType = 'existing';

            $scope.certsAvailable = ELBWizardService.certsAvailable;
            $scope.policies = ELBWizardService.policies;

            this.showTab = function (tab) {
                this.activeTab = tab;
            };

            this.chooseSSL = function () {
                $scope.certificate = this.selectedCertificate;
                ModalService.closeModal('certificateEditor');
            };

            this.uploadSSL = function () {
                CertificateService.createCertificate({
                    name: this.name,
                    privateKey: this.privateKey,
                    publicKey: this.publicKey,
                    certificateChain: this.certificateChain
                }).then(function success () {
                    ModalService.closeModal('certificateEditor');
                }, function error () {
                });
            };

            this.submitSSL = function () {
                if($scope.sslCertForm.$invalid) {
                    return;
                }

                if(this.certType === 'existing') {
                    this.chooseSSL();
                } else {
                    this.uploadSSL();
                }
            };

            this.submitBackend = function () {
            };
        }],
        controllerAs: 'ctrl'
    };
})
.directive('ifActive', function () {
    return {
        restrict: 'A',
        require: {
            certificateEditor: '^^certificateEditor',
            ngModel: 'ngModel'
        },
        link: function (scope, element, attrs, ctrls) {
            var certType = attrs.ifActive;
            var required = ctrls.ngModel.$validators.required;

            scope.$watch(function () {
                return ctrls.certificateEditor.certType;
            }, function () {
                ctrls.ngModel.$validate();
            });

            ctrls.ngModel.$validators.required = function (modelValue, viewValue) {
                if(ctrls.certificateEditor.certType !== certType) {
                    return true;
                }

                return required(modelValue, viewValue);
            };
        }
    };
})
.factory('CertificateService', ['$http', function ($http) {
    var svc = {
        getCertificates: function () {
            return $http({
                method: 'GET',
                url: '/certificate'
            }).then(function success (result) {
                return result.data && result.data.message;
            }, function error () {
                return [];
            });
        },

        createCertificate: function (cert) {
            return $http({
                method: 'POST',
                url: '/certificate',
                data: cert
            });
        }
    };

    return svc;
}]);