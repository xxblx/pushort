# -*- coding: utf-8 -*-

import os.path
from concurrent.futures import ThreadPoolExecutor

from motor import MotorClient
from tornado.web import Application

from .handlers import IndexHandler, ApiHandler, RedirectHandler


class WebApp(Application):
    def __init__(self):
        handlers = [
            (r'/', IndexHandler),
            (r'/api', ApiHandler),
            (r'/[a-zA-Z0-9]*/?', RedirectHandler)
        ]

        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        settings = {
            'template_path': template_path,
            'debug': True,
        }
        super(WebApp, self).__init__(handlers, **settings)

        # TODO: move workers, db host params and domain to config
        self.db = MotorClient(host='127.0.0.1')['pushort']
        self.executor = ThreadPoolExecutor(32)
        # FIXME
        self.short_domain = 'http://127.0.0.1:8888'
