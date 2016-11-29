"""
    Redis base:

        user:login:list - {'name': 'Name', 'pass': 'password'}
        user:login:messages - [message_id1, message_id2, ...]   - messages for only this user
        
        user:all:messages - [message_id1, message_id2, ...]   - messages for all users

        message:id - {'text': 'Text', 'from': user_login, 'to': user_login, 'time': timestamp}
"""

import json
import datetime
import time
import random
import uuid

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
import tornado.escape


class ChatHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('chat.html')


class WSHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        self.connections = set()
        super().__init__(*args, **kwargs)

    def open(self):
        # test
        self.user = {
            #'login': str(random.randint(1,100)) + 'Pavel'
            'login': 'Pavel'
        }

        self.connections.add(self)
        self.load_profile()
        self.load_users()
        self.load_messages()
        self.send_add_users([self.user])

    def on_close(self):
        self.connections.remove(self)
        self.send_remove_users([self.user])

    def on_message(self, data):
        data_dict = json.loads(data)
        if data_dict and 'message' in data_dict:
            self.save_message(data_dict['message'])

    def load_profile(self):
        self.write_message({'profile': self.user})

    def load_users(self):
        users = []
        for conn in self.connections:
            users.append(conn.user)
        self.write_message({'users': users})
                
    @tornado.gen.engine
    def load_messages(self):
        with self.application.redis.pipeline() as pipe:
            pipe.lrange('user:{}:messages'.format(self.user['login']), 0, -1)
            pipe.lrange('user:All:messages', 0, -1)
            messages = yield tornado.gen.Task(pipe.execute)
        messages = [el for lst in messages for el in lst]
        #self.write_message({'messages': messages})

    @tornado.gen.engine
    def save_to_base(self, message):
        id = str(uuid.uuid4())[:8];
        message_json = tornado.escape.json_encode(message)
        with self.application.redis.pipeline() as pipe:
            pipe.rpush('user:{}:messages'.format(message['to']), id)
            pipe.set('message:{}'.format(id), message_json)
        yield tornado.gen.Task(pipe.execute)

    def save_message(self, message):
        print(message)
        message_new = {
            'text': message['text'],
            'from': self.user['login'],
            'to': message['to'],
            'time': time.time()
        }
        self.save_to_base(message_new)
        self.send_messages([message_new])

    def send_messages(self, messages):
        for conn in self.connections:
            conn.write_message({'messages': messages})

    def send_remove_users(self, users):
        for conn in self.connections:
            conn.write_message({'remove_users': users})

    def send_add_users(self, users):
        for conn in self.connections:
            conn.write_message({'users': users})