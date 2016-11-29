
import tornado.web
import tornado.ioloop
import tornadoredis

import settings
import urls


class Application(tornado.web.Application):
    def __init__(self):
        self.redis = tornadoredis.Client(
                **settings.redis_settings,
            )
        self.redis.connect()
        super().__init__(urls.urls, **settings.tornado_settings)

def main():
    app = Application()
    app.listen(settings.tornado_settings['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()