#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop

from pushort.app import WebApp


def main():
    http_server = tornado.httpserver.HTTPServer(WebApp())
    http_server.listen(8888, '127.0.0.1')
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
