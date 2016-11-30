# -*- coding: utf-8 -*-
import tornado.web

from auth.handlers import Login, auth_async


class MainHandler(Login, tornado.web.RequestHandler):

    @auth_async
    def get(self):
        self.render('base.html')
