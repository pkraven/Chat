
import tornado.web
import tornado.ioloop

import settings
import urls


class Application(tornado.web.Application):
    def __init__(self):
        self.redis = '';

        handlers = (
            urls.urls, 
            **settings.tornado_settings
        )
        super().__init__(handlers)

def main():
    app = Application()
    app.listen(settings.options['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()