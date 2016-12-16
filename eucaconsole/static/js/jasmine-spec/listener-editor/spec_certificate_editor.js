describe('ELB Certificate Editor', function () {

    beforeEach(angular.mock.module('ELBCertificateEditorModule'));

    var $compile, $rootScope, $httpBackend;

    beforeEach(angular.mock.inject(function (_$compile_, _$rootScope_) {
        $compile = _$compile_;
        $rootScope = _$rootScope_;
    }));

    describe('certificateEditor directive', function () {

        beforeEach(inject(function ($templateCache) {
            var template = window.__html__['templates/elbs/listener-editor/certificate-editor.pt'];
            $templateCache.put('/_template/elbs/listener-editor/certificate-editor', template);
        }));

        var ModalService;
        beforeEach(inject(function ($injector) {
            ModalService = $injector.get('ModalService');
        }));

        var element, scope;
        beforeEach(function () {
            $rootScope.certificates = [];

            element = $compile(
                '<certificate-editor ng-model="certificates"></certificate-editor>'
            )($rootScope);
            $rootScope.$digest();

            scope = element.isolateScope();
        });

        describe('the controller', function () {

            var controller;
            beforeEach(function () {
                controller = element.controller('certificateEditor');
            });

            it('should default active tab', function () {
                expect(controller.activeTab).toEqual('SSL');
            });

            it('should default certificate type to existing', function () {
                expect(controller.certType).toEqual('existing');
            });

            describe('#showTab', function () {

                it('should set the tab value', function () {
                    controller.showTab('BACKEND');
                    expect(controller.activeTab).toEqual('BACKEND');
                });
            });

            describe('#uploadSSL', function () {

                it('should close modal on success', function () {
                });

                it('should update model on success', function () {
                });
            });

            describe('#chooseSSL', function () {

                beforeEach(function () {
                    controller.selectedCertificate = {server_certificate_name: 'foo', arn: 'bar'};
                    scope.certificate = {};
                    spyOn(ModalService, 'closeModal');
                });

                xit('should close modal on success', function () {
                    // Having trouble getting the correct reference here
                    // Will return
                    expect(ModalService.closeModal).toHaveBeenCalledWith('certificateEditor');
                });

                it('should update model on success', function () {
                    controller.chooseSSL();
                    expect(scope.certificate).toEqual({server_certificate_name: 'foo', arn: 'bar'});
                });
            });

            describe('#submitSSL', function () {

                beforeEach(function () {
                    spyOn(controller, 'uploadSSL');
                    spyOn(controller, 'chooseSSL');

                    scope.sslCertForm.$invalid = false;
                });

                it('should use an existing certificate when "existing" is active', function () {
                    controller.certType = 'existing';
                    controller.submitSSL();
                    expect(controller.chooseSSL).toHaveBeenCalled();
                });

                it('should upload a new certificate when "new" is active', function () {
                    controller.certType = 'new';
                    controller.submitSSL();
                    expect(controller.uploadSSL).toHaveBeenCalled();
                });

                it('should not proceed when form is invalid', function () {
                    scope.sslCertForm.$invalid = true;
                    controller.submitSSL();
                    expect(controller.chooseSSL).not.toHaveBeenCalled();
                    expect(controller.uploadSSL).not.toHaveBeenCalled();
                });
            });
        });
    });

    describe('CertificateService', function () {

        beforeEach(angular.mock.inject(function ($injector) {
            $httpBackend = $injector.get('$httpBackend');
            $httpBackend.when('GET', '/certificate').respond(
                    200, '[]');
            $httpBackend.when('POST', '/certificate').respond(
                    200, '[]');
        }));
    });
});
