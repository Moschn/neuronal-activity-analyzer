#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webgui.bootstrap import create_app

if __name__ == '__main__':
    app = create_app("webconfig.py")
    app.run(port=16290, debug=True, threaded=True)
