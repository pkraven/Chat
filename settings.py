
import os

tornado_settings = {
    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'cookie_secret': 'L9LwECiNRxq2N0N2eGxx9MZlrpmuMEimlydNX/vt1LM=',
    'login_url': '/login',
    'xsrf_cookies': True,
    'debug': True
}

redis_settings = {
    
}

options = {
    'port': 8888
}