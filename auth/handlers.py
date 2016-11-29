# -*- coding: utf-8 -*-

import random
import hashlib

import tornado.web
import tornado.gen
from tornado.escape import json_decode, json_encode, native_str


class Login():

    @tornado.gen.coroutine
    def get_user_async(self):  
        user = {}
        login = native_str(self.get_secure_cookie('login'))
        if login:
            r = self.application.redis
            user_data = yield tornado.gen.Task(r.get, 'user:{}:data'.format(login))
            if user_data:
                user_data = json_decode(user_data)
                user = {
                    'login': login,
                    'name': user_data['name']
                }
        print(user)
        return user

    def hash_pass(self, password):
        return hashlib.md5(password.encode('utf-8')).hexdigest()


class LoginHandler(Login, tornado.web.RequestHandler):

    def get(self):
        self.render('login.html')

    @tornado.gen.coroutine
    def post(self):
        login = self.get_argument('login', None)
        password = self.get_argument('password', None)

        error = ''
        if not login or not password:
            error = 'All fields must be filled.'
        else:
            r = self.application.redis
            user_data = yield tornado.gen.Task(r.get, 'user:{}:data'.format(login))
            if not user_data:
                error = 'Wrong username.'
            else:
                user_data = json_decode(user_data)
                if user_data['password'] != self.hash_pass(password):
                    error = 'Wrong password.'
                else:
                    self.set_secure_cookie('login', login)
                    self.redirect(self.reverse_url('chat'))
        self.render('login.html', error=error)


class LogoutHandler(Login, tornado.web.RequestHandler):

    def get(self):
        pass


class RegHandler(Login, tornado.web.RequestHandler):

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
                password = self.hash_pass(password)
                user_data = {
                    'name': name,
                    'password': password
                }
                yield tornado.gen.Task(r.set, 'user:{}:data'.format(login), 
                    json_encode(user_data))
                self.redirect(self.reverse_url('login'))

        self.render('reg.html', error=error)


def auth_async(method):
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        self.user = yield tornado.gen.Task(self.get_user_async)
        if not self.user:
            self.redirect(self.reverse_url('login'))
        else:
            result = method(self, *args, **kwargs)
            if result is not None:
                yield result
    return wrapper


def auth_ws_async(method):
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        self.user = yield tornado.gen.Task(self.get_user_async)
        if not self.user:
            self.write_message({'error': 'not login'})
            self.on_close()
            self.close()
        else:
            result = method(self, *args, **kwargs)
            if result is not None:
                yield result
    return wrapper


