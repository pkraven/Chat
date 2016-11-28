
import tornado.ioloop
import tornado.web
import tornado.websocket


class ChatHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.render('chat.html')


class WSHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def open(self):
        self.connections.add(self)

    def on_close(self):
        self.connections.remove(self)

    def on_message(self, data):
        data_dict = json.loads(data)
        if data_dict:
            if 'message' in data_dict:
                self.save_message(data_dict['message'])

    def load_users(self):
        users = []
        for conn in self.connections:
            users.append(conn.user)
        self.write_message({'users': users})
                
    def load_messages(self):
        messages = self.messages
        self.write_message({'messages': messages})

    def save_message(self, message):
        self.send_messages([message])

    def send_messages(self, messages):
        for conn in self.connections:
            conn.write_message({'messages': messages})

    def send_remove_users(self, users):
        for conn in self.connections:
            conn.write_message({'remove_users': users})

    def send_add_users(self, users):
        for conn in self.connections:
            conn.write_message({'users': users})