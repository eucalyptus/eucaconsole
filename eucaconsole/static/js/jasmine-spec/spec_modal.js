describe('Modal Module', function () {

    beforeEach(angular.mock.module('ModalModule'));

    var $compile, $rootScope, ModalService;

    beforeEach(angular.mock.inject(function (_$compile_, _$rootScope_, _ModalService_) {
        $compile = _$compile_;
        $rootScope = _$rootScope_;
        ModalService = _ModalService_;
    }));

    describe('modal directive', function () {

        var element, scope;
        beforeEach(function () {
            spyOn(ModalService, 'registerModal');
            spyOn(ModalService, 'closeModal');

            element = $compile(
                '<div modal="foo"><span>This is my content</span></modal>'
            )($rootScope);
            scope = element.scope();
            scope.$digest();
        });

        it('should call registerModal on compile', function () {
            expect(ModalService.registerModal).toHaveBeenCalledWith('foo', jasmine.objectContaining({
                0: jasmine.any(Object)
            }));
        });

        describe('the controller', function () {

            describe('#closeModal', function () {
                it('should call through to ModalService', function () {
                    scope.closeModal('foo');
                    expect(ModalService.closeModal).toHaveBeenCalledWith('foo');
                });
            });
        });
    });

    describe('modal service', function () {

        var scope, element;
        beforeEach(function () {
            element = $compile(
                '<div modal="foo"><span>This is my content</span></modal>'
            )($rootScope);
            scope = element.scope();
            scope.$digest();

            spyOn($rootScope, '$broadcast');
        });

        describe('#registerModal', function () {

            beforeEach(function () {
                ModalService._clearModals();
            });

            it('should add the new modal to the modal collection', function () {
                ModalService.registerModal('foo', element);

                var modalsKeys = Object.keys(ModalService._getModals());
                expect(modalsKeys.length).toEqual(1);
            });

            it('should allow multiple modals with unique names to be registered', function () {
                ModalService.registerModal('foo', element);
                ModalService.registerModal('bar', element);
                ModalService.registerModal('baz', element);

                var modalsKeys = Object.keys(ModalService._getModals());
                expect(modalsKeys.length).toEqual(3);
            });

            it('should error if a modal with that name is already registered', function () {
                ModalService.registerModal('foo', element);

                function test () {
                    // Wrapped second call in function to ease testing exception with arguments
                    ModalService.registerModal('foo', element);
                }

                expect(test).toThrowError(Error, 'Modal with name foo already registered.');
            });
        });

        describe('#openModal', function () {

            beforeEach(function () {
                ModalService._clearModals();
                ModalService.registerModal('foo', element);
            });

            it('should add the "open" class to the modal element when called', function () {
                ModalService.openModal('foo');
                expect(element.hasClass('open')).toBe(true);
            });

            it('should fire the "modal:open" event when called', function () {
                ModalService.openModal('foo');
                expect($rootScope.$broadcast).toHaveBeenCalledWith('modal:open', 'foo');
            });

            it('should not fire the "modal:open" event when called with an unregistered name', function () {
                ModalService.openModal('bar');
                expect($rootScope.$broadcast).not.toHaveBeenCalled();
            });
        });

        describe('#closeModal', function () {

            beforeEach(function () {
                ModalService._clearModals();
                ModalService.registerModal('foo', element);
                ModalService.openModal('foo');

                $rootScope.$broadcast.calls.reset();
            });

            it('should remove the "open" class from the modal element when called', function () {
                ModalService.closeModal('foo');
                expect(element.hasClass('open')).toBe(false);
            });

            it('should fire the "modal:close" event when called', function () {
                ModalService.closeModal('foo');
                expect($rootScope.$broadcast).toHaveBeenCalledWith('modal:close', 'foo');
            });

            it('should not fire the "modal:close" event when called with an unregistered name', function () {
                ModalService.closeModal('bar');
                expect($rootScope.$broadcast).not.toHaveBeenCalled();
            });
        });

        describe('#_getModals', function () {
            beforeEach(function () {
                ModalService._clearModals();
                ModalService.registerModal('foo', element);
            });

            it('should return an object containing all modal elements', function () {
                var modals = ModalService._getModals();
                expect(Object.keys(modals).length).toEqual(1);
                expect('foo' in modals).toBe(true);
            });
        });

        describe('#_clearModals', function () {
            beforeEach(function () {
                ModalService._clearModals();
                ModalService.registerModal('foo', element);
            });

            it('should clear all modals from the service', function () {
                ModalService._clearModals();

                var modals = ModalService._getModals();
                expect(Object.keys(modals).length).toEqual(0);
                expect('foo' in modals).toBe(false);
            });
        });
    });
});
