# -*- coding: utf-8 -*-
"""
    Login and Registration module
"""

import random
import hashlib
import uuid

import tornado.web
import tornado.gen
from tornado.escape import json_decode, json_encode, native_str


class Login(object):

    @tornado.gen.coroutine
    def get_user_async(self):
        user = {}
        login = native_str(self.get_secure_cookie('login'))
        if login:
            r = self.application.redis
            user_data = yield tornado.gen.Task(r.get, 'user:{}:data'.format(login))
            if not user_data:
                self.clear_all_cookies()
            else:
                token = yield tornado.gen.Task(r.get, 'user:{}:token'.format(login))
                user_data = json_decode(user_data)
                user = {
                    'login': login,
                    'name': user_data['name'],
                    'token': token
                }
        return user

    @tornado.gen.coroutine
    def get_user_ws_async(self):
        user = {}
        login = native_str(self.get_secure_cookie('login'))
        token = self.get_argument('token')
        if login and token:
            r = self.application.redis
            user_data = yield tornado.gen.Task(r.get, 'user:{}:data'.format(login))
            user_token = yield tornado.gen.Task(r.get, 'user:{}:token'.format(login))
            if user_token == token:
                user_data = json_decode(user_data)
                user = {
                    'login': login,
                    'name': user_data['name']
                }
        return user

    @staticmethod
    def hash_pass(password):
        return hashlib.md5(password.encode('utf-8')).hexdigest()


class LoginHandler(Login, tornado.web.RequestHandler):

    def get(self):
        self.render('login.html', flash={})

    @tornado.gen.coroutine
    def post(self):
        login = self.get_argument('login', None)
        password = self.get_argument('password', None)

        flash = {}
        if not login or not password:
            flash['error'] = 'All fields must be filled.'
        else:
            r = self.application.redis
            user_data = yield tornado.gen.Task(r.get, 'user:{}:data'.format(login))
            if not user_data:
                flash['error'] = 'Wrong username.'
            else:
                user_data = json_decode(user_data)
                if user_data['password'] != self.hash_pass(password):
                    flash['error'] = 'Wrong password.'
                else:
                    token = uuid.uuid4()
                    token_key = 'user:{}:token'.format(login)
                    with self.application.redis.pipeline() as pipe:
                        pipe.set(token_key, token)
                        pipe.expire(token_key, 24 * 60 * 60)
                        yield tornado.gen.Task(pipe.execute)
                    self.set_secure_cookie('login', login, expires_days=1)
                    self.redirect(self.reverse_url('chat'))

        self.render('login.html', flash=flash)


class LogoutHandler(Login, tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        login = native_str(self.get_secure_cookie('login'))
        if login:
            r = self.application.redis
            yield tornado.gen.Task(r.delete, 'user:{}:token'.format(login))
            self.clear_all_cookies()
            self.redirect(self.reverse_url('login'))


class RegHandler(Login, tornado.web.RequestHandler):

    def get(self):
        self.render('reg.html', flash={})

    @tornado.gen.coroutine
    def post(self):
        login = self.get_argument('login', None)
        name = self.get_argument('name', None)
        password = self.get_argument('password', None)

        flash = {}
        if not login or not name or not password:
            flash['error'] = 'All fields must be filled.'
        else:
            r = self.application.redis
            user = yield tornado.gen.Task(r.get, 'user:{}:data'.format(login))
            if user:
                flash['error'] = 'User "{}" already exist.'.format(login)
            else:
                password = self.hash_pass(password)
                user_data = {
                    'name': name,
                    'password': password
                }
                yield tornado.gen.Task(r.set, 'user:{}:data'.format(login),
                                       json_encode(user_data))
                flash['ok'] = 'You have been successfully registered!'

        self.render('reg.html', flash=flash)


def auth_async(method):
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        self.user = yield tornado.gen.Task(self.get_user_async)
        if not self.user:
            self.redirect(self.reverse_url('login'))
        else:
            method(self, *args, **kwargs)
    return wrapper


def auth_ws_async(method):
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        self.user = yield tornado.gen.Task(self.get_user_ws_async)
        if not self.user:
            self.write_message({'error': 'not login'})
            self.on_close()
            self.close()
        else:
            method(self, *args, **kwargs)
    return wrapper
