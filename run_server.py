#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop

from pushort.app import WebApp


def main():
    loop = tornado.ioloop.IOLoop.current()
    http_server = tornado.httpserver.HTTPServer(WebApp(loop))
    http_server.listen(8888, '127.0.0.1')

    try:
        loop.start()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
