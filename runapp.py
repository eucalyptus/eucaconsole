"""
Run app command for gunicorn
The number of workers are automatically detected based on CPU count of the host.

"""
import os
import multiprocessing

from paste.deploy import loadapp
from gunicorn.app.pasterapp import paste_server


def main():
    ini_file = 'config:console.ini'
    port = int(os.environ.get("KOALA_PORT", 8888))
    workers = multiprocessing.cpu_count() * 2 + 1
    worker_class = 'gevent'
    app = loadapp(ini_file, relative_to='.')
    paste_server(app, host='0.0.0.0', port=port, workers=workers, worker_class=worker_class)


if __name__ == "__main__":
    main()
