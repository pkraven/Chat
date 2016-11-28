
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.redirect(self.reverse_url('chat'))