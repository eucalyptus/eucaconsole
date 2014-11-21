# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.

from __future__ import with_statement

import errno
import os
import sys
from datetime import datetime
from functools import partial
import time

try:
    import gevent1
except ImportError:
    raise RuntimeError("You need gevent1 installed to use this worker.")
from gevent1.pool import Pool
from gevent1.server import StreamServer
from gevent1.socket import wait_write
from gevent1 import pywsgi

import gunicorn
from gunicorn.workers.async import AsyncWorker
from gunicorn.http.wsgi import sendfile as o_sendfile

VERSION = "gevent1/%s gunicorn/%s" % (gevent1.__version__, gunicorn.__version__)

def _gevent_sendfile(fdout, fdin, offset, nbytes):
    while True:
        try:
            return o_sendfile(fdout, fdin, offset, nbytes)
        except OSError as e:
            if e.args[0] == errno.EAGAIN:
                wait_write(fdout)
            else:
                raise

def patch_sendfile():
    from gunicorn.http import wsgi

    if o_sendfile is not None:
        setattr(wsgi, "sendfile", _gevent_sendfile)

BASE_WSGI_ENV = {
    'GATEWAY_INTERFACE': 'CGI/1.1',
    'SERVER_SOFTWARE': VERSION,
    'SCRIPT_NAME': '',
    'wsgi.version': (1, 0),
    'wsgi.multithread': False,
    'wsgi.multiprocess': False,
    'wsgi.run_once': False
}


class GeventWorker(AsyncWorker):

    server_class = None
    wsgi_handler = None

    @classmethod
    def setup(cls):
        from gevent1 import monkey
        monkey.noisy = False
        monkey.patch_all()

        # monkey patch sendfile to make it none blocking
        patch_sendfile()

    def notify(self):
        super(GeventWorker, self).notify()
        if self.ppid != os.getppid():
            self.log.info("Parent changed, shutting down: %s", self)
            sys.exit(0)

    def timeout_ctx(self):
        return gevent1.Timeout(self.cfg.keepalive, False)

    def run(self):
        servers = []
        ssl_args = {}

        if self.cfg.is_ssl:
            ssl_args = dict(server_side=True,
                    do_handshake_on_connect=False, **self.cfg.ssl_options)

        for s in self.sockets:
            s.setblocking(1)
            pool = Pool(self.worker_connections)
            if self.server_class is not None:
                server = self.server_class(
                    s, application=self.wsgi, spawn=pool, log=self.log,
                    handler_class=self.wsgi_handler, **ssl_args)
            else:
                hfun = partial(self.handle, s)
                server = StreamServer(s, handle=hfun, spawn=pool, **ssl_args)

            server.start()
            servers.append(server)

        try:
            while self.alive:
                self.notify()
                gevent1.sleep(1.0)

        except KeyboardInterrupt:
            pass
        except:
            try:
                server.stop()
            except:
                pass
            raise

        try:
            # Stop accepting requests
            for server in servers:
                if hasattr(server, 'close'): # gevent 1.0
                    server.close()
                if hasattr(server, 'kill'):  # gevent < 1.0
                    server.kill()

            # Handle current requests until graceful_timeout
            ts = time.time()
            while time.time() - ts <= self.cfg.graceful_timeout:
                accepting = 0
                for server in servers:
                    if server.pool.free_count() != server.pool.size:
                        accepting += 1

                # if no server is accepting a connection, we can exit
                if not accepting:
                    return

                self.notify()
                gevent1.sleep(1.0)

            # Force kill all active the handlers
            self.log.warning("Worker graceful timeout (pid:%s)" % self.pid)
            [server.stop(timeout=1) for server in servers]
        except:
            pass

    def handle_request(self, *args):
        try:
            super(GeventWorker, self).handle_request(*args)
        except gevent1.GreenletExit:
            pass
        except SystemExit:
            pass


class GeventResponse(object):

    status = None
    headers = None
    response_length = None

    def __init__(self, status, headers, clength):
        self.status = status
        self.headers = headers
        self.response_length = clength


class PyWSGIHandler(pywsgi.WSGIHandler):

    def log_request(self):
        start = datetime.fromtimestamp(self.time_start)
        finish = datetime.fromtimestamp(self.time_finish)
        response_time = finish - start
        resp_headers = getattr(self, 'response_headers', {})
        resp = GeventResponse(self.status, resp_headers, self.response_length)
        if hasattr(self, 'headers'):
            req_headers = [h.split(":", 1) for h in self.headers.headers]
        else:
            req_headers = []
        self.server.log.access(resp, req_headers, self.environ, response_time)

    def get_environ(self):
        env = super(PyWSGIHandler, self).get_environ()
        env['gunicorn.sock'] = self.socket
        env['RAW_URI'] = self.path
        return env


class PyWSGIServer(pywsgi.WSGIServer):
    base_env = BASE_WSGI_ENV


class GeventPyWSGIWorker(GeventWorker):
    "The Gevent StreamServer based workers."
    server_class = PyWSGIServer
    wsgi_handler = PyWSGIHandler
