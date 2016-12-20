angular.module('ELBCertificateEditorModule', ['ModalModule', 'ELBWizard'])
.directive('certificateEditor', function () {
    return {
        restrict: 'E',
        scope: {
            certificate: '=ngModel',
            backendCertificates: '='
        },
        templateUrl: '/_template/elbs/listener-editor/certificate-editor',
        controller: ['$scope', 'CertificateService', 'ModalService', 'ELBWizardService', 'eucaHandleError',
            function ($scope, CertificateService, ModalService, ELBWizardService, eucaHandleError) {
            var vm = this;
            this.activeTab = 'SSL';
            this.certType = 'existing';
            this.selectedCertificate = {};

            $scope.certsAvailable = ELBWizardService.certsAvailable;
            $scope.policies = ELBWizardService.policies;

            if ($scope.certificate.server_certificate_name) {
                this.selectedCertificate = $scope.certificate;
            }

            this.showTab = function (tab) {
                this.activeTab = tab;
            };

            this.chooseSSL = function () {
                $scope.certificate.server_certificate_name = this.selectedCertificate.server_certificate_name;
                $scope.certificate.arn = this.selectedCertificate.arn;
                ModalService.closeModal('certificateEditor');
            };

            this.uploadSSL = function () {
                CertificateService.createCertificate({
                    name: vm.name,
                    privateKey: vm.privateKey,
                    publicKey: vm.publicKey,
                    certificateChain: vm.certificateChain
                }).then(function success (result) {
                    $scope.certificate.server_certificate_name = vm.name;
                    $scope.certificate.arn = result.id;
                    ModalService.closeModal('certificateEditor');
                    Notify.success(result.message);
                }, function error(errData) {
                    eucaHandleError(errData.data.message, errData.status);
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

            this.addBackendCertificate = function () {
                $scope.backendCertificates.push({
                    name: vm.backendCertificateName,
                    certificateBody: vm.backendCertificateBody
                });
                vm.backendCertificateName = '';
                vm.backendCertificateBody = '';
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
            }).then(function success (result) {
                return result.data;
            });
        }
    };

    return svc;
}]);
