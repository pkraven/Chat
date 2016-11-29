# -*- coding: utf-8 -*-

import random
import hashlib

import tornado.web
import tornado.gen
from tornado.escape import json_decode, json_encode


class Login():

    def get_current_user_async(self, callback):  
        id = str(random.randint(1,100))
        user = {
            'login': id + 'pk@gmail.com',
            'name': id + 'Pavel'
        }
        user=''
        callback(user)


class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('login.html')


class LogoutHandler(tornado.web.RequestHandler):

    def get(self):
        pass


class RegHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('reg.html', error='')

    @tornado.gen.coroutine
    def post(self):
        login = self.get_argument('login', None)
        name = self.get_argument('name', None)
        password = self.get_argument('password', None)
        
        error = ''
        if not login or not name or not password:
            error = 'All fields must be filled.'
        else:
            r = self.application.redis
            user = yield tornado.gen.Task(r.get, 'user:{}:data'.format(login))
            if user:
                error = 'User "{}" already exist.'.format(login)
            else:
                password = hashlib.md5(password.encode('utf-8')).hexdigest()
                user_data = {
                    'name': name,
                    'password': password
                }
                yield tornado.gen.Task(r.set, 'user:{}:data'.format(login), 
                    json_encode(user_data))
                self.redirect(self.reverse_url('login'))

        self.render('reg.html', error=error)


def auth_async(method):
    @tornado.gen.engine
    def wrapper(self, *args, **kwargs):
        self.user = yield tornado.gen.Task(self.get_current_user_async)
        if not self.user:
            self.redirect(self.reverse_url('login'))
        else:
            result = method(self, *args, **kwargs)
            if result is not None:
                yield result
    return wrapper


def auth_ws_async(method):
    @tornado.gen.engine
    def wrapper(self, *args, **kwargs):
        self.user = yield tornado.gen.Task(self.get_current_user_async)
        if not self.user:
            self.write_message({'error': 'not login'})
            self.on_close()
            self.close()
        else:
            result = method(self, *args, **kwargs)
            if result is not None:
                yield result
    return wrapper


