#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent.wsgi import WSGIServer
from webgui.bootstrap import create_app

if __name__ == '__main__':
    app = create_app("webconfig.py")
    http_server = WSGIServer(('', 16290), app)
    http_server.serve_forever()
