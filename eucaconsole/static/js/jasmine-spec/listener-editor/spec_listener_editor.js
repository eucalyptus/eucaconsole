describe('ELB Listener Editor', function () {

    beforeEach(angular.mock.module('ELBListenerEditorModule'));

    var $compile, $rootScope, $httpBackend;

    beforeEach(angular.mock.inject(function (_$compile_, _$rootScope_) {
        $compile = _$compile_;
        $rootScope = _$rootScope_;
    }));

    describe('listenerEditor directive', function () {

        beforeEach(angular.mock.inject(function ($injector) {
            $httpBackend = $injector.get('$httpBackend');
            $httpBackend.when('GET', '/_template/elbs/listener-editor/listener-editor').respond(
                    200, '');
        }));

        var element, scope;
        beforeEach(function () {
            element = $compile(
                '<listener-editor></listener-editor>'
            )($rootScope);
            $rootScope.$digest();
            $httpBackend.flush();

            scope = element.isolateScope();
        });

        describe('the controller', function () {

            var controller;
            beforeEach(function () {
                controller = element.controller('listenerEditor');
            });

            it('should default client and instance-side port configurations to empty', function () {
                expect(controller.from).toEqual({});
                expect(controller.to).toEqual({});
            });

            describe('#clientSideValid', function () {

                it('should return false when client-side port and protocol are not set', function () {
                    var res = controller.clientSideValid();
                    expect(res).toBe(false);
                });

                it('should return true when client-side port and protocol are valid', function () {
                    controller.from = {
                        port: 80,
                        protocol: 'HTTP'
                    };

                    var res = controller.clientSideValid();
                    expect(res).toBe(true);
                });

                it('should return false when client-side port or protocol are invalid', function () {
                    controller.from = {
                        protocol: 'HTTP'
                    };

                    var res = controller.clientSideValid();
                    expect(res).toBe(false);
                });
            });

            describe('#portsValid', function () {

                it('should return false when both client and instance-side configurations are not set', function () {
                    var res = controller.portsValid();
                    expect(res).toBe(false);
                });

                it('should return true when both client and instance-side configurations are valid', function () {
                    controller.from = {
                        port: 80,
                        protocol: 'HTTP'
                    };

                    controller.to = {
                        port: 80,
                        protocol: 'HTTP'
                    };

                    var res = controller.portsValid();
                    expect(res).toBe(true);
                });

                it('should return false when client or instance-side configurations are invalid', function () {
                    controller.from = {
                        port: 80
                    };

                    controller.to = {
                        port: 80,
                        protocol: 'HTTP'
                    };

                    var res = controller.portsValid();
                    expect(res).toBe(false);
                });
            });

            describe('#removeListener', function () {

                beforeEach(function () {
                    scope.listeners = ['one', 'two', 'three'];
                });

                it('should remove the appropriate listener configuration', function () {
                    controller.removeListener(1);
                    expect(scope.listeners).toEqual(['one', 'three']);
                });
            });

            describe('#addListener', function () {

                beforeEach(function () {
                    controller.from = {
                        port: 80,
                        protocol: 'HTTP'
                    };

                    controller.to = {
                        port: 80,
                        protocol: 'HTTP'
                    };

                    scope.listeners = [];
                });

                it('should add a new listener to the listeners array when valid', function () {
                    controller.addListener();
                    expect(scope.listeners.length).toEqual(1);
                });

                it('should not add a new listener to the listeners array when invalid', function () {
                    controller.to = {}; // invalid case
                    controller.addListener();
                    expect(scope.listeners.length).toEqual(0);
                });

                it('should reset directive from and to values', function () {
                    controller.addListener();
                    expect(controller.from).toEqual({});
                    expect(controller.to).toEqual({});
                });
            });
        });
    });

    describe('protocolPort directive', function () {

        beforeEach(angular.mock.inject(function ($injector) {
            $httpBackend = $injector.get('$httpBackend');
            $httpBackend.when('GET', '/_template/elbs/listener-editor/protocol-port').respond(
                    200, '');
        }));

        var element, scope;
        beforeEach(function () {
            $rootScope.model = {
                port: 80,
                protocol: 'HTTP'
            };

            element = $compile(
                '<protocol-port ng-model="model" label="My Label"></protocol-port>'
            )($rootScope);
            $rootScope.$digest();
            $httpBackend.flush();

            scope = element.isolateScope();
        });

        it('should display the value of the label attribute', function () {
            expect(scope.label).toEqual('My Label');
        });

        it('should accept and map the value of its model', function () {
            expect(scope.target).toEqual({
                port: 80,
                protocol: 'HTTP'
            });
        });

        describe('the controller', function () {

            var controller;
            beforeEach(function () {
                controller = element.controller('protocolPort');
            });

            it('should default list of available ports and protocols', function () {
                expect(controller.protocols).toEqual(jasmine.any(Array));
            });

            describe('#onUpdate', function () {

                it('should set the correct port when a protocol is selected', function () {
                    controller.onUpdate({
                        protocol: 'FOO',
                        port: 1000
                    });
                    expect(scope.port).toEqual(1000);
                });
            });
        });
    });
});
