# -*- coding: utf-8 -*-
"""
    WebSocket-Chat
    
    Structure Redis base:
        user:login:data = dump{'name': 'Name', 'password': 'password'}
        user:login:messages_sent = [message_id1, message_id2, ...]   # my messages to special user
        user:login:messages_received = [message_id1, message_id2, ...]   # special user message to me
        user:login:token = token   # token for websocket authorization
        
        user:all:messages = [message_id1, message_id2, ...]   # messages for all users

        message:id = dump{'text': 'Text', 'from': user_login, 'to': [user_login, ..], 'time': timestamp, 'date': Date}
"""

import tornado.web
import tornado.ioloop
import tornadoredis

import settings
import urls


class Application(tornado.web.Application):

    def __init__(self):
        self.connections = []
        self.redis = tornadoredis.Client(
            **settings.redis_settings
        )
        self.redis.connect()
        super().__init__(urls.urls, **settings.tornado_settings)


def main():
    app = Application()
    app.listen(settings.tornado_settings['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
