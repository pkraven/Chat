
from tornado.web import url
from main.handlers import MainHandler 
from auth.handlers import LoginHandler, LogoutHandler, RegHandler
from wschat.handlers import ChatHandler, WSHandler

urls = [
    url(r"/", MainHandler, name="main"),
    url(r"/chat", ChatHandler, name="chat"),
    url(r"/ws", WSHandler),
    url(r"/login", LoginHandler, name="login"),
    url(r"/logout", LogoutHandler, name="logout"),
    url(r"/reg", RegHandler, name="reg"),
]