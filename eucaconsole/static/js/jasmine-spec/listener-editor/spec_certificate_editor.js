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

                it('should not submit when form is invalid', function () {
                });

                it('should close modal on success', function () {
                });

                it('should update model on success', function () {
                });
            });

            describe('#chooseSSL', function () {

                it('should not submit when form is invalid', function () {
                });

                it('should close modal on success', function () {
                });

                it('should update model on success', function () {
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
