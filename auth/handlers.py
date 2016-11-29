
import random

import tornado.web
import tornado.gen


class Login():
    def get_current_user_async(self, callback):  
        id = str(random.randint(1,100))
        user = {
            'login': id + 'pk@gmail.com',
            'name': id + 'Pavel'
        }
        callback(user)


class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("")


class LogoutHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("")


class RegHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("")


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