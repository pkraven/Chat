# -*- coding: utf-8 -*-
"""
    WebSocket chat module
"""

import datetime
import time
import uuid

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.escape import json_decode, json_encode

from auth.handlers import Login, auth_async, auth_ws_async


class ChatHandler(Login, tornado.web.RequestHandler):
    """Render chat template"""

    @auth_async
    def get(self):
        self.render('chat.html', user=self.user)


class WebSocketHandler(Login, tornado.websocket.WebSocketHandler):
    """Main websocket class"""

    @auth_ws_async
    def open(self):
        print(self.get_argument('token'))
        self.application.connections.append(self)
        self.load_profile()
        self.load_users()
        self.load_messages()
        self.add_user(self.user)

    def on_close(self):
        for key, conn in enumerate(self.application.connections):
            if conn == self:
                del self.application.connections[key]
        self.remove_user(self.user)

    def on_message(self, data):
        data_dict = json_decode(data)
        if data_dict and 'message' in data_dict:
            self.save_message(data_dict['message'])

    def load_profile(self):
        self.write_message({'profile': self.user})

    def load_users(self):
        users = []
        for conn in self.application.connections:
            if conn.user != self.user:
                users.append(conn.user)
        self.write_message({'users': users})

    @tornado.gen.coroutine
    def load_messages(self):
        with self.application.redis.pipeline() as pipe:
            pipe.lrange('user:{}:messages_sent'.format(
                self.user['login']), 0, 30)
            pipe.lrange('user:{}:messages_received'.format(
                self.user['login']), 0, 30)
            pipe.lrange('user:all:messages', 0, 30)
            messages_id = yield tornado.gen.Task(pipe.execute)
            messages_id = [el for lst in messages_id for el in lst]
        if messages_id:
            with self.application.redis.pipeline() as pipe:
                for id in messages_id:
                    pipe.get('message:{}'.format(id))
                messages = yield tornado.gen.Task(pipe.execute)
                messages = [json_decode(message) for message in messages]
            self.write_message({'messages': messages})

    def save_message(self, message):
        message = {
            'text': message['text'],
            'from': self.user['login'],
            'to': message['to'],
            'time': time.time(),
            'date': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_to_base(message)
        self.send_messages([message])

    @tornado.gen.coroutine
    def save_to_base(self, message):
        with self.application.redis.pipeline() as pipe:
            id = str(uuid.uuid4())[:8]
            pipe.set('message:{}'.format(id), json_encode(message))
            if not message['to']:
                pipe.lpush('user:all:messages', id)
            else:
                pipe.lpush('user:{}:messages_sent'.format(message['from']), id)
                for login in message['to']:
                    pipe.lpush('user:{}:messages_received'.format(login), id)
            yield tornado.gen.Task(pipe.execute)

    def send_messages(self, messages):
        for conn in self.application.connections:
            conn.write_message({'messages': messages})

    def add_user(self, user):
        for conn in self.application.connections:
            if conn.user != self.user:
                conn.write_message({'users': [user]})

    def remove_user(self, user):
        for conn in self.application.connections:
            conn.write_message({'remove_users': [user]})