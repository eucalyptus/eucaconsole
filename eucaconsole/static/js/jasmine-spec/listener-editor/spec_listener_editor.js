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
            $rootScope.listeners = [];

            element = $compile(
                '<listener-editor ng-model="listeners"></listener-editor>'
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

            it('should default list of available ports and protocols', function () {
                expect(controller.protocols).toEqual(jasmine.any(Array));
            });

            it('should default client and instance-side port configurations to empty', function () {
                expect(controller.from).toEqual({});
                expect(controller.to).toEqual({});
            });

            describe('#sourceValid', function () {

                it('should return false when client-side port and protocol are not set', function () {
                    var res = controller.sourceValid({
                    });
                    expect(res).toBe(false);
                });

                it('should return true when client-side port and protocol are valid', function () {
                    var res = controller.sourceValid({
                        port: 80,
                        protocol: 'HTTP'
                    });
                    expect(res).toBe(true);
                });

                it('should return false when client-side port or protocol are invalid', function () {
                    var res = controller.sourceValid({
                        protocolo: 'HTTP'
                    });
                    expect(res).toBe(false);
                });
            });

            describe('#targetValid', function () {

                it('should return false when server-side port and protocol are not set', function () {
                    var res = controller.targetValid({
                    });
                    expect(res).toBe(false);
                });

                it('should return true when server-side port and protocol are valid', function () {
                    var res = controller.targetValid({
                        port: 80,
                        protocol: 'HTTP'
                    });
                    expect(res).toBe(true);
                });

                it('should return false when server-side port and protocol are invalid', function () {
                    var res = controller.targetValid({
                        protocolo: 'HTTP'
                    });
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
                        port: 80,
                        protocol: 'None'
                    };

                    controller.to = {
                        port: 80,
                        protocol: 'HTTP'
                    };

                    var res = controller.portsValid();
                    expect(res).toBe(false);
                });
            });

            describe('#portInUse', function () {

                beforeEach(function () {
                    scope.listeners = [{
                        'fromPort': 80,
                        'toPort': 80,
                        'fromProtocol': 'HTTP',
                        'toProtocol': 'HTTP'
                    }];
                });

                it('should return true if the target port is in use', function () {
                    var res = controller.portInUse({
                        port: '80'
                    });

                    expect(res).toBe(true);
                });

                it('should return false if the target port is not currently in use', function () {
                    var res = controller.portInUse({
                        port: '81'
                    });

                    expect(res).toBe(false);
                });
            });

            describe('#portOutOfRange', function () {

                it('should return true if reserved port is not in acceptable range', function () {
                    var res = controller.portOutOfRange({
                        port: '81'
                    });
                    expect(res).toBe(true);
                });

                it('should return false if reserved port is in acceptable range', function () {
                    var res = controller.portOutOfRange({
                        port: '80'
                    });
                    expect(res).toBe(false);
                });

                it('should return true if unreserved port is not in acceptable range', function () {
                    var res = controller.portOutOfRange({
                        port: '1023'
                    });
                    expect(res).toBe(true);
                });

                it('should return false if unreserved port is in acceptable range', function () {
                    var res = controller.portOutOfRange({
                        port: '1025'
                    });
                    expect(res).toBe(false);
                });

                it('should accept undefined as a value if allowEmpty is true', function () {
                    var res = controller.portOutOfRange({}, true);
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

                    spyOn(controller, 'reset');
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
                    expect(controller.reset).toHaveBeenCalled();
                });
            });

            describe('#reset', function () {
                it('should set "from" and "to" listener settings to defaults', function () {
                    controller.reset();
                    expect(controller.from).toEqual(controller.protocols[0]);
                    expect(controller.to).toEqual(controller.protocols[0]);
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
