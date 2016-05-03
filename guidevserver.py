#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webgui.bootstrap import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, threaded=True)
