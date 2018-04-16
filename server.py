#coding:utf-8
""""
Program: chat
Description: 
Author: XY - mailyanxin@gmail.com
Date: 2018-04-14 03:39:27
Last modified: 2018-04-16 08:02:44
Python release: 3.5.2
"""

import os
import json
import logging

import tornado.web
from tornado import gen

from tornado.options import parse_command_line
from tornado.options import define, options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from message_helper import MessageBuffer


define('server_host', default='0.0.0.0', help='server host')
define('server_port', default=8000, help='server port')
define('mysql_host', default='localhost', help='mysql host')
define('mysql_pwd', default='dddd', help='mysql password')
define('debug', default=True, help='debug')






global_message_buffer = MessageBuffer()



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', messages= user_message_buffer.cache)


class MessageNewHandler(tornado.web.RequestHandler):
    def post(self):
        data = self.request.body.decode('utf-8')
        params = json.loads(data)

        ret_data = global_message_buffer.new_messages(
                from_user_id = params['from_user_id'],
                target_user_id = params['target_user_id'],
                data = params['data'],
                )

        ret = {
                'errcode': 0,
                'errmsg': 'ok',
                'data': {'id':ret_data.id},
                }
        self.write(ret)

class MessageUpdateHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        data = self.request.body.decode('utf-8')
        params = json.loads(data)

        self.future = global_message_buffer.wait_for_message(
                wait_from_user_id = params['from_user_id'],
                wait_target_user_id = params['target_user_id'],
                cursor=params.get('cursor',None),
                )
        message = yield self.future
        if self.request.connection.stream.closed():
            self.write('closed')
        ret = {
                'errcode': 0,
                'errmsg': 'ok',
                'data': message
                }
        self.write(ret)


def create_app():
    settings = {
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
            'static_path': os.path.join(os.path.dirname(__file__), "static"),
            'debug': options.debug,
            }

    handler_dispatch = [
            (r"/", MainHandler),
            (r"/a/message/new", MessageNewHandler),
            (r"/a/message/update", MessageUpdateHandler),
            ]

    app = tornado.web.Application(handler_dispatch, **settings)
    return app

def main():
    parse_command_line()
    app = create_app()
    server = HTTPServer(app)
    server.bind(options.server_port,address=options.server_host)
    server.start(1)
    IOLoop.current().start()

if __name__ == '__main__':
    main()

